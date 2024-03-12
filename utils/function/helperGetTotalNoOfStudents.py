
from datetime import timedelta, datetime
from django.utils import timezone


def get_total_no_of_student_by_program(program,offering_mode):
    unique_students = set()
    if offering_mode=="online":
        # program_offerings = program.program_offerings.all().filter(offering_mode = "online")
        for course in program.courses.all():
            for course_offering in course.course_offerings.all().filter(offering_mode = 'online'):
                    students_in_course = course_offering.student.all()
                    unique_students.update(students_in_course)  
    elif offering_mode=="offline":
        
        # program_offerings = program.program_offerings.all().exclude(offering_mode = "online")
        for course in program.courses.all():
            for course_offering in course.course_offerings.all().exclude(offering_mode = 'online'):
                    students_in_course = course_offering.student.all()
                    unique_students.update(students_in_course)  
    elif offering_mode=="all":
        # program_offerings=program.program_offerings.all()
        for course in program.courses.all():
            for course_offering in course.course_offerings.all():
                    students_in_course = course_offering.student.all()
                    unique_students.update(students_in_course)

    # for program_offering in program_offerings:
    #     students_in_program = program_offering.student.all()
    #     unique_students.update(students_in_program)
 
    return unique_students

def get_total_no_of_student_by_course(course, offering_mode):
    unique_students = set()
    if offering_mode=="online":
        course_offerings=course.course_offerings.all().filter(offering_mode = 'online')
    elif offering_mode=="offline":
        course_offerings=course.course_offerings.all().exclude(offering_mode = 'online')
    elif offering_mode=="all":
        course_offerings=course.course_offerings.all()

    for course_offering in course_offerings:
        students_in_course = course_offering.student.all()
        unique_students.update(students_in_course)
    # print('total _Stunt cousre ',len(unique_students))
    return unique_students

def get_total_no_of_student_by_courses(courses, offering_mode):
    unique_students = set()
    if courses:
        for course in courses:
            if offering_mode=="online":
                students_in_course=get_total_no_of_student_by_course(course, offering_mode='online')
            elif offering_mode=="offline":
                students_in_course=get_total_no_of_student_by_course(course, offering_mode='offline')
            elif offering_mode=="all":
                students_in_course=get_total_no_of_student_by_course(course, offering_mode='all')

            unique_students.update(students_in_course)

  
    return unique_students




def get_total_no_of_student_by_program_offerings(program_offerings):
    # this method has duplicate values dont use 
    student_count=0
    for program_offering in program_offerings:
        st_in_pro_offering=program_offering.student.count()
        student_count=student_count+st_in_pro_offering

    return student_count

def get_total_unique_no_of_student_by_program_offerings(program_offerings):
    if program_offerings:
        students=set()
        for program_offering in program_offerings:
            st_in_pro_offering=program_offering.student.all()
            students.update(st_in_pro_offering)
        
        return students
    else:
        return None

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
