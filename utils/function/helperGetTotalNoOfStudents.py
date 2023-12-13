
from datetime import timedelta, datetime
from django.utils import timezone



def get_total_no_of_student_by_program_offerings(program_offerings):
    # this method has duplicate values dont use 
    student_count=0
    for program_offering in program_offerings:
        st_in_pro_offering=program_offering.student.count()
        student_count=student_count+st_in_pro_offering

    return student_count

def get_total_unique_no_of_student_by_program_offerings(program_offerings):
    students=set()
    for program_offering in program_offerings:
        st_in_pro_offering=program_offering.student.all()
        students.update(st_in_pro_offering)
    
    return students

def get_total_no_of_student_by_course_offerings(course_offerings):
    # this method has duplicate values dont use 
    student_count=0
    for course_offering in course_offerings:
        st_in_course_offering=course_offering.student.count()
        student_count=student_count+st_in_course_offering

    return student_count

def get_total_unique_no_of_student_by_course_offerings(course_offerings):
    students=set()
    for course_offering in course_offerings:
        st_in_course_offering=course_offering.student.all()
        students.update(st_in_course_offering)
    
    return students
