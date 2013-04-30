import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF
import random
from classify.classifying import Classifier
from pyres import ResQ

from model import session as db_session, Users, Stories, FC, CC, Queue
from classifying import *

r = ResQ()

sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}

# seed db! open rss file, read it, parse it, create object, 
# add obj to session, commit, and repeat til done

def load_stories(source, session):
	# use feedparser to grab & parse the rss feed
	parsed = feedparser.parse(sources[source])
	# go through each entry in the RSS feed to pull out elements for Stories
	for i in range(len(parsed.entries)):
		title = parsed.entries[i].title
		url = parsed.entries[i].link
		source = source
		# pull abstract, parse out extra crap that is sometimes included 
		abstract = (parsed.entries[i].description.split('<'))[0]
		# connect with db
		story = model.Stories(title=title, url=url, abstract=abstract, source=source)
		# add story to db
		session.add(story)
		# commit 
		session.commit()

class Probabilities():
	# set queue for load_queue jobs
	queue = 'probability'
	# static method to integrate with pyres
	@staticmethod
	def load_queue(session, user_id):
		
		stories = db_session.query(Stories).all()
		queue = {}
		for item in stories:
			# determine probability that the user will like this item
			doc =  Classifier.gettext(item.url) # words
			# artwords = Classifier.getwords(Classifier.gettext(item.url))
			cl = FisherClassifier(Classifier.getwords) # returns instance 
			cl.setdb('news.db')
			classification = 'yes'

			# determine probability that user will like it
			# TO DO: throw in a test for this coming back all screwy!
			probability = cl.fisherprob(doc, classification, user_id)
			print probability
			# add item's probability to the queue dictionary
			queue[item.id]=probability
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






def main(session):
	# for item in sources:
	# 	load_stories(item, session)

	Probabilities.load_queue(session, 1)

if __name__ == "__main__":
	s = model.session
	main(s)