from apscheduler.schedulers.blocking import BlockingScheduler
from main import run
if __name__=="__main__":
    s=BlockingScheduler(timezone="UTC")
    for hour in (7,10,13,15,18): s.add_job(run,"cron",hour=hour,minute=5,kwargs={"official":True},max_instances=1,coalesce=True)
    s.start()

