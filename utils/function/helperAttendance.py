
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
    return 0.0


def get_attendance_percentage_by_program(program,total_sessions,present_sessions):
    total_sessions=total_sessions
    present_sessions=present_sessions
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


def get_attendance_percentage_by_course(course,total_sessions,present_sessions):
        if course.temp_id[-1] == "D":
            return "Not Applicable"
        else:
            total_sessions=total_sessions
            present_sessions=present_sessions
            course_offerings=course.course_offering.all()
            for course_offering in course_offerings:
                total_sessions+=course_offering.attendance.count()
                present_sessions += course_offering.attendance.filter(is_present='present').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_attendance_percentage_by_course_offering(course_offering, total_sessions, present_sessions):
        if course_offering.offering_mode == "online":
            return "Not Applicable"
        else:
            total_sessions=course_offering.attendance.count()
            present_sessions = course_offering.attendance.filter(is_present='present').count()
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
        all_attendances=student.attendances.all()
        total_sessions=all_attendances.count()
        present_sessions=all_attendances.filter(is_present='present').count()
    

        return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)




     
     