import re
import math
import sqlite3 as sqlite
import sys
from sys import argv
from decruft import Document
import urllib2
from pyquery import PyQuery
from lxml import etree


def gettext(url):
	# use decruft methods to grab article from page html
	f = urllib2.urlopen(url)
	html = (Document(f.read()).summary())
	# use pyquery to get rid of all markup: just leave article text
	doc = PyQuery(html)
	article =  doc.text()
	return article 

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

# This class encapsulates what the classifier has learned so far
# With this, we can instantiate multiple classifiers for different 
# users, groups, or queries & can train differently to respond to 
# particular needs
class classifier:
	def __init__(self, getfeatures):

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

	# method that opens the dbfile for this classifier and creates
	# tables if necessary
	def setdb(self, dbfile):
		self.con = sqlite.connect(dbfile)
		self.con.execute('create table if not exists fc(feature, category, count)')
		self.con.execute('create table if not exists cc(category, count)')

	# HELPER FUNCTIONS!!!! --> interact w/database
	
	# increase count of a feature/category pair by 1 in fc table
	def incf(self, f, cat):
		count = self.fcount(f, cat)
		if count == 0:
			self.con.execute("INSERT INTO fc VALUES ('%s', '%s', 1)" % (f, cat))
		else:
			self.con.execute("UPDATE fc SET count=%d WHERE feature='%s' and category='%s'" % (count+1, f, cat))

	# number of times a feature has appeared in a category in fc table
	def fcount(self, f, cat):
		res = self.con.execute("SELECT count FROM fc WHERE feature='%s' AND category='%s'" %(f, cat)).fetchone()
		if res == None:
			return 0
		else:
			return float(res[0])

	# increase the count of a category in cc table
	def incc(self, cat):
		count = self.catcount(cat)
		if count == 0:
			self.con.execute("INSERT INTO cc VALUES ('%s', 1)" % (cat))
		else:
			self.con.execute("UPDATE cc SET count=%d WHERE category='%s'"%(count+1, cat))

	# query db for current category count
	def catcount(self, cat):
		res = self.con.execute("SELECT count FROM cc WHERE category='%s'"%(cat)).fetchone()
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

	# train method: takes doc item and a classification (in our case, yes or no). Uses 
	# getfeatures func to break items into separate features, then increases counts for this 
	# classification for each feature, then increases total count for classification
	def train(self, item, cat):
		features = self.getfeatures(item)
		# increment count for every feature with this category
		for f in features:
			self.incf(f, cat)
		# increment count for this category
		self.incc(cat)
		# save to db
		self.con.commit()

	# calculate probability that a word is in yes or no cats by dividing
	# the number of times the word appears in a doc in that cat by total number
	# of docs in that cat?
	def fprob(self, f, cat):
		# check to see the current count of category occurances
		if self.catcount(cat)==0: 
			return 0
		# total number of times this feature appeared in this category divided by total items in this category
		# Pr(A|B) --> conditional probability
		return self.fcount(f, cat)/self.catcount(cat)

	# calculate a weighted probabiity with an assumed probability of 0.5
	def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
		# calculate current probability
		basicprob = prf(f, cat)
		# count times the feature has appeared in all categories
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
class fisherclassifier(classifier):
	# init method w/variable to store cutoffs
	def __init__(self, getfeatures):
		classifier.__init__(self, getfeatures)
		self.minimums={}

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
		features = self.getfeatures(item)
		for f in features:
			p *= (self.weightedprob(f, cat, self.cprob))\
		# take natural log and multiply by -2
		fscore = -2*math.log(p)
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

	# calculate probabilites for each category and determine the best
	# result that exceeds the specified minimum
	def classify(self, item, default=None):
		# loop through looking for best result
		best = default
		max = 0.0
		for c in self.categories():
			p = self.fisherprob(item, c)
			# make sure it exceeds its minimum
			if p > self.getminimum(c) and p > max:
				best = c
				max = p
		return best

def main():
    args = argv
    script, url, learn_guess, classification = args

    if learn_guess == 'train':
    	doc = gettext(url)
    	cl = fisherclassifier(getwords)
    	cl.setdb('test1.db')
    	cl.train(doc, classification)
    	print 'trained that db'

    if learn_guess == 'guess':
    	doc = gettext(url)
    	cl = fisherclassifier(getwords)
    	cl.setdb('test1.db')
    	print "Test article classified as " + cl.classify(doc)
    	print cl.fisherprob(doc, classification), classification

if __name__ == "__main__":
    main()