# from apscheduler.scheduler import Scheduler
import requests
# import redis
# from rq import Queue, use_connection

# use_connection()
# q = Queue(connection=conn)

# sched = Scheduler()

# @sched.interval_schedule(seconds=30)

def load_stories():
    # enqueue rss_load job to RQ!

	sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}
	for source in sources:
		print source
		# use feedparser to grab & parse the rss feed
		parsed = feedparser.parse(sources[source])
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
			# add story to db
			session.add(story)
			# commit 
			session.commit()
			print "committed"


# q = Queue()
# q.enqueue(load_stories)

# sched.start()
