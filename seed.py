import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF
import random
from model import session as db_session, Users, Stories, Preferences, Queue


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

def load_queue(session):
	stories = db_session.query(Stories).all()
	queue = {}
	for item in stories:
		# assign a random score between 0.0 and 1.0 to story
		# this (obviously) will also change once algorithm in place
		queue[item.id]=random.random()
	# by iterating through dict as (key, val) tuples, find items rated above 0.95 & put them in a list of story_ids
	high = [key for (key, value) in queue.items() if value>0.97]
	for i in high:
		story_id = i
		score = queue[i]
		# go ahead and add this nonsense to the queue table in the db: will I need this? I have no idea. 
		story = Queue(story_id=story_id, score=score)
		db_session.add(story)
		db_session.commit()
	#grab some that are rated lower?
	low = [key for (key, value) in queue.items() if 0.75<value<0.77]
	for i in low:
		story_id = i
		score = queue[i]
		# go ahead and add this nonsense to the queue table in the db: will I need this? I have no idea. 
		story = Queue(story_id=story_id, score=score)
		db_session.add(story)
		db_session.commit()




def main(session):
	# for item in sources:
	# 	load_stories(item, session)

	load_queue(session)

if __name__ == "__main__":
	s = model.session
	main(s)