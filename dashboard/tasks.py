from celery import shared_task
from time import sleep
 

@shared_task(name="test task subtration")
def sub(x,y):
    sleep(10)
    return x-y

@shared_task(name="period task test 1")
def periodic_task_test():
    # sleep(2)
    x= " task 1 complete"
    print(" periodic task 1 completed :",x)

    return 
 
@shared_task(name="period task test 2")
def periodic_task_test2():
    # sleep(2)
    x= " task 2 complete"
    print(" periodic task 2 completed :",x)
 
    return x
 
@shared_task(name='student_attendance_engagement_action_report_generation_task')
def student_attendance_engagement_action_report_generation():
    return 