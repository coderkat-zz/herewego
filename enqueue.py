from redis import Redis
from rq import Queue
from rqfun import load_stories
from apscheduler.scheduler import Scheduler 

sched = Scheduler()


q = Queue(connection=Redis())

import model
import sqlalchemy.exc
from model import session as db_session, Stories 

@sched.interval_schedule(hours=3)
def result():
	q.enqueue(load_stories, model.session)

sched.start()

