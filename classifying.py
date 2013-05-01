import re
import math
import sqlite3 as sqlite
import sys
from sys import argv
from decruft import Document
import urllib2
from pyquery import PyQuery
from pyres import ResQ
import time
from model import session as db_session, Users, Stories, FC, CC, Queue
import sqlalchemy.exc
import feedparser

r = ResQ()


# This class encapsulates what the classifier has learned so far
# With this, we can instantiate multiple classifiers for different 
# users, groups, or queries & can train differently to respond to 
# particular needs
class Classifier:
	# queue method to work with pyres, defines a queue for classify actions
	queue = "training"

	def __init__(self, getfeatures, user_id):
		self.user_id = user_id

		# fc stores counts for different features in diferent 
		# classifications: {'python':{'bad':0, 'good':6}...}
		self.fc = {}

		# cc: dict of hwo many times each classification has
		# been used -> needed for probability calculations
		self.cc = {}

		# function used to extract features from the items
		# being classified (here, it's the getwords funct)

		# TODO: UNDERSTAND THIS CONNECTION????
		self.getfeatures = getfeatures

	@staticmethod
	def gettext(url):
		# use decruft methods to grab article from page html
		f = urllib2.urlopen(url)
		html = (Document(f.read()).summary())

		# use pyquery to get rid of all markup: just leave article text
		doc = PyQuery(html)
		article = doc.text()
		return article

	@staticmethod
	def getwords(doc):
		# list of common words we want to ignore from our corpus
		commonWords = ('the','be','to','of','and','a','in','that','have','it','is','im','are','was','for','on','with','he','as','you','do','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like','time','just','him','know','take','person','into','year','your','some','could','them','see','other','than','then','now','look','only','come','its','over','think','also','back','after','use','two','how','our','way','even','because','any','these','us')
		# split word by non-alpha characters	
		# TODO: also remove numbers??
		splitter = re.compile('\\W*')
		# lowercase all words, discount short & common words
		words = [s.lower() for s in splitter.split(doc) if len(s)>2 and s not in commonWords and not s.isdigit()]
		# return a list of words from source
		return words

	@staticmethod 
	def perform(url, classification):
		# TO DO: Integrate user_id
		
		# grab article text, parse out markup and return list of significant words
		artwords = Classifier.getwords(Classifier.gettext(url))
		print "got the list of words"
		# need to make a Classifier instance in order to reference a class method
		classifier = Classifier(artwords)
		# set up db (or connect if exists)
		classifier.setdb('news.db')
		print "connect with the database"
		# train db w/new words and their classifications
		for item in artwords:
			classifier.train(item, classification)
		print "trained that database"

	# method that opens the dbfile for this classifier and creates
	# tables if necessary
	def setdb(self, dbfile):
		self.con = sqlite.connect(dbfile)


	# HELPER FUNCTIONS!!!! --> interact w/database
	
	# increase count of a feature/category pair by 1 in fc table
	def incf(self, f, cat):
		count = self.fcount(f, cat)
		if count == 0:
			self.con.execute("INSERT INTO fc VALUES (NULL, '%s', '%s', 1, %d)" % (f, cat, self.user_id))
		else:
			self.con.execute("UPDATE fc SET count=%d WHERE feature='%s' AND category='%s' AND user_id=%d" % (count+1, f, cat, self.user_id))

	# number of times a feature has appeared in a category in fc table
	def fcount(self, f, cat):
		res = self.con.execute("SELECT count FROM fc WHERE feature='%s' AND category='%s' AND user_id=%d" %(f, cat, self.user_id)).fetchone()
		if res == None:
			return 0
		else:
			return res[0]

	# increase the count of a category in cc table
	def incc(self, cat):
		count = self.catcount(cat)
		if count == 0:
			self.con.execute("INSERT INTO cc VALUES (NULL, '%s', 1, %d)" % (cat, self.user_id))
		else:
			self.con.execute("UPDATE cc SET count=%d WHERE category='%s' AND user_id=%d"%(count+1, cat, self.user_id))

	# query db for current category count
	def catcount(self, cat):
		# print "what category did I pass in, again?"
		# print cat
		res = self.con.execute("SELECT count FROM cc WHERE category='%s' AND user_id=%d"%(cat, self.user_id)).fetchone()
		# above line WAS fetchall() a la collective intelligence
		# print "CURRENT CATEGORY COUNT"
		# print cat
		# print user_id
		# print res[0]
		if res == None:
			return 0
		else:
			return float(res[0])

	# the list of all existing categories:
	def categories(self):
		cur = self.con.execute("SELECT category FROM cc");
		return [d[0] for d in cur]

	# total number of items
	def totalcount(self):
		res = self.con.execute("SELECT sum(count) FROM cc").fetchone();
		if res == None:
			return 0
		else:
			return res[0]

	# train method: takes doc item (a word in our case) and a classification 
	# (in our case, yes or no). Uses getfeatures func to break items into separate features,
	# then increases counts for this classification for each feature, then increases total 
	# count for classification
	def train(self, item, cat):
		# increment count the item of this category
		self.incf(item, cat)
		# increment count for this category
		self.incc(cat)
		# # mark user id for each thing
		# self.userid(user_id)
		# save to db
		self.con.commit()

	# calculate probability that a word is in yes or no cats by dividing
	# the number of times the word appears in a doc in that cat by total number
	# of docs in that cat?
	def fprob(self, f, cat):
		# print "self.catcount --> "
		# print self.catcount
		# print "now we do stuff --> "
		# print self.catcount(cat, user_id)
		# check to see the current count of category occurances
		if self.catcount(cat)==0: 
			return 0
		# total number of times this feature appeared in this category divided by total items in this category
		# Pr(A|B) --> conditional probability
		# print "we return -->"
		# print self.fcount(f, cat, user_id)/self.catcount(cat, user_id)
		return self.fcount(f, cat)/self.catcount(cat) #works! theoretically

	# calculate a weighted probabiity with an assumed probability of 0.5
	def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
		# calculate current probability FOR THIS USER
		basicprob=prf(f, cat)
		# count times the feature has appeared in all categories FOR THIS USER
		totals = sum([self.fcount(f,c) for c in self.categories()])
		# calculate weighted average
		bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
		return bp 

#################################################################################
# Fisher classifier: begin by calculating how likely it is that a doc fits into
# a certian category given that a particular feature is in that dcument (Pr(cat|feature))
# Considers normalization (given uneven categorization):
# clf = Pr(feature|category) for this category
# freqsum = Sum of Pr(feature|category) for ALL categories
# cprob = clf / (clf + nclf)
###############################################################################
class FisherClassifier(Classifier):
	
	# queue method to work with pyres, defines a queue for classify actions
	# moved this to feedseed.py (which then talks to this doc)
	# queue = "predict"

	# init method w/variable to store cutoffs
	def __init__(self, getfeatures, user_id):
		Classifier.__init__(self, getfeatures, user_id)
		self.minimums={}
	

	# classify and pull relevant news stories for user's feed!
	@staticmethod 
	def perform(user_id):
		print user_id
		stories = db_session.query(Stories).all()
		print "got stories"
		queue = {}
		for item in stories:
			# determine probability that the user will like this item
			doc =  Classifier.gettext(item.url) # strong of article words
			cl = FisherClassifier(Classifier.getwords, user_id) # returns instance 
			cl.setdb('news.db')
			classification = 'yes'
			print "Ready to Classify!!!"

			# determine probability that user will like it
			# TO DO: throw in a test for this coming back all screwy!
			probability = cl.fisherprob(doc, user_id)

			print "Got the probability that you'll looove this -->"
			print probability
			# add item's probability to the queue dictionary
			queue[item.id]=probability
			print "Articles: aquired! -->"
			print queue


		# by iterating through dict as (key, val) tuples, find items rated above 0.97 & put them in a list of story_ids
		high = [key for (key, value) in queue.items() if value>0.97]
		for i in high:
			story_id = i
			score = queue[i]	
			# add story, user, and probabiilty to the db for pulling articles for users
			story = Queue(story_id=story_id, score=score, user_id=user_id)
			db_session.add(story)
			db_session.commit()
		
		#grab some that are rated lower
		low = [key for (key, value) in queue.items() if 0.75<value<0.77]
		for i in low:
			story_id = i
			score = queue[i]
			# add story, user, and probabiilty to the db for pulling articles for users
			story = Queue(story_id=story_id, score=score, user_id=user_id)
			db_session.add(story)
			db_session.commit()


	# set mins and get values (default to 0)
	def setminimum(self, cat, min):
		self.minimums[cat] = min
	def getminimum(self, cat):
		if cat not in self.minimums:
			return 0
		return self.minimums[cat]

	def cprob(self, f, cat):
		# frequency of this feature in this category
		clf = self.fprob(f, cat)
		if clf == 0: 
			return 0
		# frequency of this feature in all categories
		freqsum = sum([self.fprob(f,c) for c in self.categories()])
		# probability is the frequency in this category divided by overall frequency
		p = clf / (freqsum)
		return p # the probability that an item w/feature belongs in specified category, assuming equal items in each cat.

	# estimate overall probability: mult all probs together, take log, mult by -2
	def fisherprob(self, item, cat):
		# multiply all probabilities together
		p = 1
		features = self.getwords(item) # list of words
		print "got words: items in a list"
		print features

		for f in features: # iterate through list
			print f
			p *= (self.weightedprob(f, cat, self.cprob)) 
			print p   # OH NOES. SOMETIMES GETS TO ZERO.
		# WHICH IS WHY FSCORE BREAKS. WTF HAPPENED.
		# Note: does not happen on all articles.

		# take natural log and multiply by -2
		fscore = (-2)*math.log(p)

		# use inverse chi2 function to get a probability
		return self.invchi2(fscore, len(features)*2)

	# inverse chi-square function
	# by feeding fisher calculation to this, we get the probability that
	# a random  set of probabilities would return a high number for 
	# an item belonging in the category (eq. from CI book, p. 130)
	def invchi2(self, chi, df):
		m = chi / 2.0
		sum = term = math.exp(-m)
		for i in range(1, df//2):
			term *= m / i
			sum += term
		return min(sum, 1.0)

	## UH THIS IS NEVER USED NOW?? MAKE SURE BEFORE REMOVING
	# # calculate probabilites for each category and determine the best
	# # result that exceeds the specified minimum
	# def classify(self, item, user_id, default=None):
	# 	# loop through looking for best result
	# 	best = default
	# 	max = 0.0
	# 	for c in self.categories():
	# 		p = self.fisherprob(item, c)
	# 		print p
	# 		# make sure it exceeds its minimum
	# 		if p > self.getminimum(c) and p > max:
	# 			best = c
	# 			max = p
	# 	return best

def main():
	print "Main 1"
	# FisherClassifier.perform(url="http://www.bbc.co.uk/news/technology-22368287", user_id=0)

	

if __name__ == "__main__":
    main()
