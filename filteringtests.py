import re
import math

# small sample training corpus
def sampletrain(cl):
	cl.train('Nobody owns the water.', 'good')
	cl.train('the quick rabbit jumps fences', 'good')
	cl.train('buy pharmaceuticals now', 'bad')
	cl.train('make quick money at the online casino', 'bad')
	cl.train('the quick brown fox jumps', 'good')


def getwords(doc):
	splitter = re.compile('\\W*')
	# split word by non-alpha characters
	words = [s.lower() for s in splitter.split(doc) if len(s)>2 and len(s)<20]

	# return only the unique set of words
	return dict([(w, 1) for w in words])

class classifier:
	def __init__(self, getfeatures, filename=None):
		classifier.__init__(self, getfeatures)
		self.thresholds={}
		# counts of features/cat combination
		self.fc = {}
		# counts of docs in each category
		self.cc = {}
		self.getfeatures = getfeatures

	# set and get threshold values
	def setthreshold(self, cat, t):
		self.thresholds[cat]=t

	def getthreshold(self, cat):
		if cat not in self.thresholds: return 1.0
		return self.thresholds[cat]

	# increase count of a feature/category pair
	def incf(self, f, cat):
		self.fc.setdefault(f, {})
		self.fc[f].setdefault(cat, 0)
		self.fc[f][cat] += 1

	# increase the count of a category
	def incc(self, cat):
		self.cc.setdefault(cat, 0)
		self.cc[cat] += 1

	# number of times a feature has appeared in a category
	def fcount(self, f, cat):
		if f in self.fc and cat in self.fc[f]:
			return float(self.fc[f][cat])
		return 0.0

	# number of items in a category
	def catcount(self, cat):
		if cat in self.cc:
			return float(self.cc[cat])
		return 0

	# total number of items
	def totalcount(self):
		return sum(self.cc.values())

	# the list of all categories:
	def categories(self):
		return self.cc.keys()

	# break item into features, increase counts on every feature, increases classification count
	def train(self, item, cat):
		features = self.getfeatures(item)
		# increment count for every feature with this category
		for f in features:
			self.incf(f, cat)

		# increment count for this category
		self.incc(cat)

	# determine probabilitythat a word is in a particular category
	def fprob(self, f, cat):
		if self.catcount(cat)==0: return 0
		# total number of times this feature appeared in this category divided by total items in this category
		# Pr(A|B) --> conditional probability
		return self.fcount(f, cat)/self.catcount(cat)

	# set up assumed probability and calculate weighted average
	def weightedprob(self,f,cat,prf,weight=1.0,ap=0.5):
		# calculate current probability
		basicprob=prf(f, cat)

		# count number of times feature appears in all categories
		totals = sum([self.fcount(f, c) for c in self.categories()])

		# calculate weighted average
		bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
		return bp 

	# calculate probability for each category and determine which is largest: does that exceed the next 
	# largest by more than its threshold?
	def classify(self, item, default=None):	
	probs={}
		# find category with highest probability
		max=0.0
		for cat in self.categories():
			probs[cat]=self.prob(item, cat)
			if probs[cat]>max:
				max=probs[cat]
				best=cat 
		# make sure probability exceeds threshold*next best
		for cat in probs:
			if cat==best: continue
			if probs[cat]*self.getthreshold(best)>probs[best]: return default
		return best

class naivebayes(classifier):
	def docprob(self,item,cat):
		features = self.getfeatures(item)

		# multiply probabilities of all features together
		p=1
		for f in features: p*=self.weightedprob(f, cat, self.fprob)
		return p

	# calculate probablilty of the category
	def prob(self, item, cat):
		catprob = self.catcount(cat)/self.totalcount()
		docprob = self.docprob(item, cat)
		return docprob*catprob
