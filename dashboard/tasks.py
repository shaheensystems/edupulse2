from celery import shared_task
from time import sleep
from collections import Counter

@shared_task(name="test task subtration")
def sub(x,y):
    sleep(10)
    return x-y
@shared_task(name="test task 2 subtration")
def sub2(x,y):
    sleep(5)
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
