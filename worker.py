from rq import Queue, use_connection
use_connection()
q = Queue()

from clock import load_stories



result = q.enqueue(load_stories)


