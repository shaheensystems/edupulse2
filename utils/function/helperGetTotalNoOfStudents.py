
from datetime import timedelta, datetime
from django.utils import timezone
from django.db import connection
from django.db.models import Prefetch

# wrong method 
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





def get_all_student_enrollments_by_program_offering(program_offering):
    
    # connection.queries.clear()
    
    student_enrollments=program_offering.student_enrollments.all()
    # print("Number of queries executed:", len(connection.queries), " for student enrollments count :",len(student_enrollments))
    #  # Check if the prefetch cache is populated for student enrollments
    # prefetch_cache = getattr(program_offering, '_prefetched_objects_cache', {})
    # has_prefetch = 'student_enrollments' in prefetch_cache

    # # print("Number of queries executed:", len(connection.queries))
    # print("Has prefetch for student_enrollments:", has_prefetch)
    
    total_enrolled_students = []
    total_enrolled_students = [enrollment.student for enrollment in student_enrollments]
    # connection.queries.clear()
    # connection.queries.clear()
    # print("Number of queries cleared:", len(connection.queries))
    # print("Content of connection.queries after clearing:", connection.queries)
    
    # for student_enrollment in student_enrollments:
    #     enrolled_student=student_enrollment.student
    #     total_enrolled_students.append(enrolled_student)
    
    # return enrolled_students
    return total_enrolled_students
   
def get_all_student_enrollments_by_program(program,offering_mode):
    # students enrollments allow count duplicate students enrolled in program too
    total_enrolled_students = []
    if offering_mode=='all':
        program_offerings=program.program_offerings.all()
    elif offering_mode =='online':
        program_offerings=program.program_offerings.all().filter(offering_mode  = 'online')
    elif offering_mode == 'offline':
        program_offerings=program.program_offerings.all().exclude(offering_mode  = 'online')
    
    for program_offering in program_offerings:
        # enrolled_students=program_offering.calculate_total_student_enrollments()
        
        enrolled_students = get_all_student_enrollments_by_program_offering(program_offering)
        
        total_enrolled_students.extend(enrolled_students)
    
    return total_enrolled_students 

def get_all_student_enrollments_by_course_offering(course_offering):
    total_enrolled_students = []
    
    student_enrollments=course_offering.student_enrollments.all()
    
    
    for student_enrollment in student_enrollments:
        enrolled_student=student_enrollment.student
        total_enrolled_students.append(enrolled_student)
        
        
    # print(f"course offering :{course_offering} and student enrollment :{len(student_enrollments)} for total student :{len(total_enrolled_students)}")   
    #     print(f"Student enrolled in program offering {program_offering}: { enrolled_student}")
        
    # print(f"Total Enrolled students by program Offering {program_offering} :{len(total_enrolled_students)}")
    # print(f"Total Enrolled students by program Offering {program_offering} :{len(set(total_enrolled_students))}")
    
    
    return total_enrolled_students
 



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
    if course_offerings:
        for course_offering in course_offerings:
            st_in_course_offering=course_offering.student.all()
            students.update(st_in_course_offering)
    
    return students
