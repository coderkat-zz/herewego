from pyres import ResQ
from pyres_scheduler import PyresScheduler
from pyres_scheduler.decorators import periodic_task, timedelta

pyres_sched = PyresScheduler()
resque = ResQ()
pyres_sched.add_resque(resque)


@periodic_task(priority='high', run_every=timedelta(seconds=60))
def my_task():
    print 'Executing task'

pyres_sched.start()

pyres_sched.add_job(my_task)

# check version of pyres_scheduler

