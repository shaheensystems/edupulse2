
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from utils.function.BaseValues_List import ATTENDANCE_CHOICE





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
    courses = program.courses.all().exclude(temp_id__endswith='D')
    # print("Course list offline",courses)

   
    # Iterate over each course to accumulate session counts
    for course in courses:
        course_offerings=course.course_offerings.all()
        if course_offerings:
            for course_offering in course_offerings:
                if course_offering.offering_mode=="online":
                     print("error calculating attendance")
                else:
                    total_sessions+=course_offering.attendances.count()
                    present_sessions += course_offering.attendances.filter(is_present='present').count()

    return get_attendance_percentage(present_sessions,total_sessions)   
 
def get_engagement_percentage_by_program(program,offering_mode):
    total_sessions=0
    present_sessions=0
    # print("Course list all",program.course.all())
    if offering_mode=='online':
        courses = program.courses.all().filter(temp_id__endswith='D')
    elif offering_mode=='blended':
        courses = program.courses.all().exclude(temp_id__endswith='D')
    else:
        print('offering Mode is not selected properly')
        return "Error in Offering Mode "
    # print("Course list offline",courses)

   
    # Iterate over each course to accumulate session counts
    for course in courses:
        course_offerings=course.course_offerings.all()
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
            course_offerings=course.course_offerings.all()
            for course_offering in course_offerings:
                total_sessions+=course_offering.attendances.count()
                present_sessions += course_offering.attendances.filter(is_present='present').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)
        
def get_engagement_percentage_by_course(course):
        
            total_sessions=0
            present_sessions=0
            course_offerings=course.course_offerings.all()
            for course_offering in course_offerings:
                total_sessions+=course_offering.weekly_reports.count()
                present_sessions += course_offering.weekly_reports.exclude(engagement='na').count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_engagement_percentage_by_course_offering(course_offering):
        
            total_sessions=0
            present_sessions=0
            total_sessions+=course_offering.weekly_reports.count()
            present_sessions += course_offering.weekly_reports.exclude(Q(engagement='na')|Q(engagement='n/a')).count()

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_engagement_percentage_by_student(student):
            total_sessions=0
            present_sessions=0
            
            weekly_reports=student.weekly_reports.all()
            # total_sessions=course_offering.weekly_reports.count()
            total_sessions=weekly_reports.count()
            # for wr in weekly_reports:
            #     print(wr.student)
            #     print(wr.engagement)
            
            
            # present_sessions += course_offering.weekly_reports.exclude(engagement='na').count()
            present_sessions = weekly_reports.exclude(Q(engagement='na')|Q(engagement='n/a')).count()
            
            # print(total_sessions,":",present_sessions)

            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)
    
def get_engagement_percentage_by_course_offering_for_student(course_offering,student):
        
            total_sessions=0
            present_sessions=0
            
            weekly_reports=course_offering.weekly_reports.filter(student=student)
            # total_sessions=course_offering.weekly_reports.count()
            total_sessions=weekly_reports.count()
            for wr in weekly_reports:
                print(wr.student)
                print(wr.engagement)
            
            
            # present_sessions += course_offering.weekly_reports.exclude(engagement='na').count()
            present_sessions = weekly_reports.exclude(Q(engagement='na')|Q(engagement='n/a')).count()
            
            print(course_offering,"-",total_sessions,":",present_sessions)

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
            present_sessions = len(course_offering.attendances.filter(is_present='present'))
            absent_sessions=len(course_offering.attendances.exclude(is_present='present'))
            total_sessions=present_sessions+absent_sessions
            
            
            return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_attendance_percentage_by_program_offering(program_offering,total_sessions,present_sessions):
    # Get all the courses associated with the program
        if program_offering.offering_mode == "online":
            return "Not Applicable"
        courses = program_offering.program.courses.all()

        for course in courses:
            course_offerings = course.course_offerings.all()
           
            # course_offerings=course.course_offerings.all()        
            if course_offerings:                  
                for course_offering in course_offerings:
                    total_sessions += course_offering.attendances.count()
                    # below line is creating multiple query 
                    present_sessions += course_offering.attendances.filter(is_present='present').count()
                   
        return get_attendance_percentage(present_sessions=present_sessions, total_sessions=total_sessions)

def get_attendance_percentage_by_student(student):
    # Get all the courses associated with the program
        all_attendances=student.attendances.exclude(course_offering__offering_mode='online')
        total_sessions=all_attendances.count()
        present_sessions=all_attendances.filter(is_present='present').count()
    

        return get_attendance_percentage(present_sessions=present_sessions,total_sessions=total_sessions)

def get_students_attendance_report_by_students(students):
    all_attendance_count = 0
    present_count = 0
    absent_count = 0
    informed_absent_count = 0
    tardy_count = 0
    # Define a list of colors for each category
    category_colors = ['#FF5733', '#33FF57', '#FFFF33', '#FF33EE']  # Example colors


    for student in students:
        new_attendances = student.attendances.exclude(course_offering__offering_mode='online')
        all_attendance_count += new_attendances.count()
        present_count += new_attendances.filter(is_present="present").count()
        absent_count += new_attendances.filter(is_present="absent").count()
        informed_absent_count += new_attendances.filter(is_present="informed absent").count()
        tardy_count += new_attendances.filter(is_present="tardy").count()

    # Calculate percentages
    present_percentage = 0 if all_attendance_count == 0 else (present_count / all_attendance_count) * 100
    absent_percentage = 0 if all_attendance_count == 0 else (absent_count / all_attendance_count) * 100
    informed_absent_percentage = 0 if all_attendance_count == 0 else (informed_absent_count / all_attendance_count) * 100
    tardy_percentage = 0 if all_attendance_count == 0 else (tardy_count / all_attendance_count) * 100

    # Create a list of dictionaries representing each category and its corresponding percentage
    student_attendance_percentage = [
        {'category': 'Present', 'percentage': present_percentage, 'color': category_colors[0]},
        {'category': 'Absent', 'percentage': absent_percentage, 'color': category_colors[1]},
        {'category': 'Informed Absent', 'percentage': informed_absent_percentage, 'color': category_colors[2]},
        {'category': 'Tardy', 'percentage': tardy_percentage, 'color': category_colors[3]},
    ]

    return student_attendance_percentage

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



def record_attendance(student_obj,course_offering_obj,attendance_date,is_present_value,week_number):
    
    from report.models import Attendance,WeeklyReport
    print(f"Start recording attendance as per detail : {course_offering_obj}-{student_obj} on {attendance_date} is {is_present_value}")
  
    if is_present_value.lower() not in [choice[0] for choice in ATTENDANCE_CHOICE]:
        print("Error: is_present value does not exist in attendance choices")
            
    
    
    if student_obj.student_enrollments.filter(course_offering=course_offering_obj).exists():
        new_attendance, created =Attendance.objects.get_or_create(
            course_offering=course_offering_obj,
            student=student_obj,
            attendance_date=attendance_date,
            is_present=is_present_value.lower()
        )
        new_attendance.save()
        
        print(f"new attendance recorded : {new_attendance}:{new_attendance.is_present}")
        # now generate weekly report
        if week_number>0 :
            weekly_report , created=WeeklyReport.objects.get_or_create(
                student=student_obj,
                course_offering=course_offering_obj,
                week_number=week_number
            )
            if not weekly_report.sessions.filter(Q(id=new_attendance.id)).exists():
                weekly_report.sessions.add(new_attendance)
            else:
                print("attendance already exits in weekly report")
            
            weekly_report.save()
    else:
        print("error !!! student is not enrolled in selected course_offering ")
            
     
     