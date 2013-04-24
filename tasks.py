from celery import Celery 
import model
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'tasks.add',
        'schedule': timedelta(seconds=30),
        'args': (16, 16)
    },
}

CELERY_TIMEZONE = 'UTC'
# 1st arg: name of current module, 2nd: url of broker
celery = Celery('tasks', backend='redis://localhost', broker='redis://localhost')
source = 'http://feeds.bbci.co.uk/news/rss.xml'


@celery.task
def add(x, y):
    return x + y

# @celery.task
# def load_stories(source, session):
# 		# seed db! open rss file, read it, parse it, create object, 
# 		# add obj to session, commit, and repeat til done
# 	print source
# 	# use feedparser to grab & parse the rss feed
# 	parsed = feedparser.parse(sources[source])
# 	print parsed
# 	# go through each entry in the RSS feed to pull out elements for Stories
# 	for i in range(len(parsed.entries)):
# 		title = parsed.entries[i].title
# 		print "Did we get it??"
# 		print title
# 		url = parsed.entries[i].link
# 		source = source
# 		# pull abstract, parse out extra crap that is sometimes included 
# 		abstract = (parsed.entries[i].description.split('<'))[0]
# 		# connect with db
# 		story = model.Stories(title=title, url=url, abstract=abstract, source=source)
# 		# add story to db
# 		session.add(story)
# 		# commit 
# 		session.commit()
# 		print "all done"
