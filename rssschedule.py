import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF
import random
from model import session as db_session, Users, Stories, Preferences, Queue

from pyres import ResQ 
from pyres_scheduler import PyresScheduler 
from pyres_scheduler.decorators import periodic_task, timedelta
import feedseed

sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}


pyres_sched = PyresScheduler()
resque = ResQ()
pyres_sched.add_resque(resque)

@periodic_task(priority='high', run_every=timedelta(hours=3))
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
   

def main(session):
	pyres_sched.start()
	for source in sources:
		pyres_sched.add_job(load_stories) #DOES NOT WORD (whole 5-args thing)

if __name__ == "__main__":
	s = model.session
	main(s)

