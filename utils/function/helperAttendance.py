
from datetime import timedelta, datetime
from django.utils import timezone




def get_attendance_percentage(present_sessions,total_sessions):
     # Check if there are any sessions before calculating the percentage to avoid division by zero
    if total_sessions > 0:
        # Calculate the attendance percentage as (present_sessions / total_sessions) * 100
        attendance_percentage = (present_sessions / total_sessions) * 100

        # Round the percentage to two decimal places for better readability
        return round(attendance_percentage, 2)

    # If there are no sessions, return 0.0 as the default attendance percentage
    return 00.00


def get_attendance_percentage_by_program(program):
    total_sessions=0
    present_sessions=0
    # print("Course list all",program.course.all())
    courses = program.course.all().exclude(temp_id__endswith='D')
    # print("Course list offline",courses)

   
    # Iterate over each course to accumulate session counts
    for course in courses:
        course_offerings=course.course_offering.all()
        if course_offerings:
            for course_offering in course_offerings:
                if course_offering.offering_mode=="online":
                     print("error calculating attendance")
                else:
                    total_sessions+=course_offering.attendance.count()
                    present_sessions += course_offering.attendance.filter(is_present='present').count()

    return get_attendance_percentage(present_sessions,total_sessions)   
 
def get_engagement_percentage_by_program(program,offering_mode):
    total_sessions=0
    present_sessions=0
    # print("Course list all",program.course.all())
    if offering_mode=='online':
        courses = program.course.all().filter(temp_id__endswith='D')
    elif offering_mode=='blended':
        courses = program.course.all().exclude(temp_id__endswith='D')
    else:
        print('offering Mode is not selected properly')
        return "Error in Offering Mode "
    # print("Course list offline",courses)

   
    # Iterate over each course to accumulate session counts
    for course in courses:
        course_offerings=course.course_offering.all()
        if course_offerings:
            for course_offering in course_offerings:
                    total_sessions+=course_offering.weekly_reports.count()
                    present_sessions += course_offering.weekly_reports.exclude(engagement='na').count()

    return get_attendance_percentage(present_sessions,total_sessions)    


def get_attendance_percentage_by_course(course):
        if course.temp_id[-1] == "D":
            return "Not Applicable"
        else:
            total_sessions=0
            present_sessions=0
            course_offerings=course.course_offering.all()
            for course_offering in course_offerings:
                total_sessions+=course_offering.attendance.count()
                present_sessions += course_offering.attendance.filter(is_present='present').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)
        
def get_engagement_percentage_by_course(course):
        
            total_sessions=0
            present_sessions=0
            course_offerings=course.course_offering.all()
            for course_offering in course_offerings:
                total_sessions+=course_offering.weekly_reports.count()
                present_sessions += course_offering.weekly_reports.exclude(engagement='na').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_attendance_percentage_by_course_offering(course_offering, total_sessions, present_sessions):
        if course_offering.offering_mode == "online":
            return "Not Applicable"
        else:
            
            # get 100 query each method 
            # total_sessions=course_offering.attendance.count()
            # present_sessions = course_offering.attendance.filter(is_present='present').count()
            
            # total_sessions = len(course_offering.present_attendance) + len(course_offering.absent_attendance)
            # present_sessions = len(course_offering.present_attendance)
            # print("present_attendance:",course_offering.attendance.filter(is_present='present'))
            present_sessions = len(course_offering.attendance.filter(is_present='present'))
            absent_sessions=len(course_offering.attendance.exclude(is_present='present'))
            total_sessions=present_sessions+absent_sessions
            
            
            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_attendance_percentage_by_program_offering(program_offering,total_sessions,present_sessions):
    # Get all the courses associated with the program
        if program_offering.offering_mode == "online":
            return "Not Applicable"
        else:
            total_sessions=total_sessions
            present_sessions=present_sessions
            courses = program_offering.program.course.all()

            for course in courses:
                course_offerings=course.course_offering.all()           
                if course_offerings:                
                    for course_offering in course_offerings:
                        total_sessions += course_offering.attendance.count()
                        present_sessions += course_offering.attendance.filter(is_present='present').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_attendance_percentage_by_student(student):
    # Get all the courses associated with the program
        all_attendances=student.attendances.exclude(course_offering__offering_mode='online')
        total_sessions=all_attendances.count()
        present_sessions=all_attendances.filter(is_present='present').count()
    

        return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)
    

def get_attendance_percentage_by_attendances(attendances):
    
    
    if len(attendances)==0:
        return 0
    else:
        offline_attendance=attendances.exclude(course_offering__offering_mode="online")
        # offline_attendance=attendances
        total_sessions=len(offline_attendance)
        # getting query 200 plus 
        present_sessions=len(offline_attendance.filter(is_present='present'))
        # total_sessions=0
        # present_sessions=0
        # print(get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions))
        return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)



     
     