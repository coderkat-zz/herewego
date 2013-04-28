from datetime import datetime
from apscheduler.scheduler import Scheduler
import model
from model import session as db_session, Users, Stories, Preferences, Queue
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF
# from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
from apscheduler.jobstores.shelve_store import ShelveJobStore
    

sched = Scheduler()
sched.add_jobstore(ShelveJobStore('/tmp/dbfile'), 'file')
# sched.add_jobstore(SQLAlchemyJobStore('/tmp/dbfile'), 'file')
sched.start()


# sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}


# seed db! open rss file, read it, parse it, create object, 
# add obj to session, commit, and repeat til done
@sched.interval_schedule(minutes=3)
def load_stories():

	sources = {"BBC":'http://feeds.bbci.co.uk/news/rss.xml'}
	for source in sources:
		print source
		# use feedparser to grab & parse the rss feed
		parsed = feedparser.parse(sources[source])
		print "parsed"
		# go through each entry in the RSS feed to pull out elements for Stories
		for i in range(len(parsed.entries)):
			title = parsed.entries[i].title
			url = parsed.entries[i].link
			source = source
			# pull abstract, parse out extra crap that is sometimes included 
			abstract = (parsed.entries[i].description.split('<'))[0]
			print abstract

			# connect with db
			story = model.Stories(title=title, url=url, abstract=abstract, source=source)
			print "connected with db model??"
			# add story to db
			session.add(story)
			print "added story to db"
			# commit 
			session.commit()
			print "committed"
