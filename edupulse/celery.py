import os

from celery import Celery
from time import sleep
from datetime import timedelta
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edupulse.settings')

app = Celery('edupulse')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    
    
@app.task
def add(x,y):
    sleep(10)
    return x+y

@app.task
def delete_all_periodic_tasks(name="delete all periodic task"):
    from django_celery_beat.models import PeriodicTask, PeriodicTasks
    # Find the periodic task by name and delete it
    tasks_to_delete = PeriodicTask.objects.all()
    deleted_count = tasks_to_delete.delete()[0]  # Get the number of deleted tasks
    PeriodicTasks.update_changed()  # Notify celery beat about the changes
    print(f"Deleted {deleted_count} tasks")
    
@app.task
def delete_all_tasks(name='delete all task result '):
    from django_celery_results.models import TaskResult
    # Find the periodic task by name and delete it
    tasks_to_delete = TaskResult.objects.all()
    deleted_count = tasks_to_delete.delete()[0]  # Get the number of deleted tasks
   
    print(f"Deleted {deleted_count} tasks")
    
app.conf.beat_schedule = {
    'every-1-min': {
        'task': 'edupulse.celery.delete_all_tasks',  # Ensure this matches the actual task path
        'schedule': 60,  # Run every 60 seconds
    },
}

# # periodic task method 2 
# app.conf.beat_schedule ={
#      "every-10-seconds":{
#         'task':'dashboard.tasks.periodic_task_test',
#         # 'schedule':10,
#         # 'schedule':timedelta(seconds=10 ),
#         'schedule':crontab(minute='*/1 ') ,
#         'args':('1111',)
        
#     },
# }
