
from datetime import timedelta, datetime
from django.utils import timezone





def get_last_week_dates():
    current_date = datetime.now().date()

    # Calculate the start and end dates for the last week
    end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
    start_date_last_week = end_date_last_week - timedelta(days=6)

    return start_date_last_week,end_date_last_week

def get_last_week_WeeklyReport():
    from report.models import WeeklyReport
    current_date = datetime.now().date()

    # Calculate the start and end dates for the last week
    end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
    start_date_last_week = end_date_last_week - timedelta(days=6)

    weekly_reports_for_last_week=WeeklyReport.objects.filter(
        sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
    )

    return weekly_reports_for_last_week

def get_at_risk_student_list_by_filter(start_date,end_date,students,course_offering):
    from report.models import WeeklyReport
    at_risk_students=set()
    # no of query from 23 to 942 and with select related and prefetch related is raise from 23 to 942
    # print("students :",students)
    # for student in students:
    #     weekly_reports_list=WeeklyReport.objects.filter(
    #         student=student,
    #         course_offering=course_offering,
    #         sessions__attendance_date__range=[start_date, end_date]
    #     )
    #     if weekly_reports_list:
    #             for weekly_report in  weekly_reports_list:
    #                 if weekly_report.at_risk is True:
    #                     # adding one object in set 
    #                     at_risk_students.add(student)
    
    # no of query from 23 to 85 in below method
    # weekly_reports=WeeklyReport.objects.select_related('student', 'course_offering').prefetch_related('sessions').all()
    # weekly_reports_list = weekly_reports.filter(
    # course_offering=course_offering,
    # sessions__attendance_date__range=[start_date, end_date],
    # at_risk=True,
    # student__in=students
    # )
    
    weekly_reports_list = course_offering.weekly_reports.select_related('student', 'course_offering').prefetch_related('sessions').filter(
        sessions__attendance_date__range=[start_date, end_date],
        at_risk=True,
        student__in=students
    )


    # this alone function is querying from 26 to 85 
    for weekly_report in weekly_reports_list:
        at_risk_students.add(weekly_report.student)
        


    return at_risk_students

def get_all_at_risk_student_last_week(students):
    from report.models import WeeklyReport

    start_date,end_date=get_last_week_dates()
  
    at_risk_students=set()

    # print("students :",students)
    for student in students:
        weekly_reports_list=WeeklyReport.objects.filter(
            student=student,
            sessions__attendance_date__range=[start_date, end_date]
        )
        if weekly_reports_list:
                for weekly_report in  weekly_reports_list:
                    if weekly_report.at_risk is True:
                        # adding one object in set 
                        at_risk_students.add(student)

    return at_risk_students




def get_no_of_at_risk_students_by_program(program):

    # Get all courses associated with the program
    courses = program.courses.all()

    # Initialize variable to track the count of at-risk students
    at_risk_students = set()
        # Get all students associated with the course offering
    # print("count students :",students.count())
    # Iterate over each course to accumulate session counts
    for course in courses:
        at_risk_students_new=get_no_of_at_risk_students_by_course(course=course)     
        at_risk_students.update(at_risk_students_new)

    return at_risk_students

# from onr program Offering 
def get_no_of_at_risk_students_by_program_offering(program_offering):
        at_risk_students = set()
        # Get all courses associated with the program
        courses = program_offering.program.courses.all()

        # Iterate over each course to accumulate session counts
        for course in courses:
            at_risk_students_new=get_no_of_at_risk_students_by_course(course=course)
            at_risk_students.update(at_risk_students_new)
               
        return at_risk_students

# from query set of multiple program Offering 
def get_no_of_at_risk_students_by_program_offerings(program_offerings):

        at_risk_students = set()
        # Get all courses associated with the program
        for program_offering in program_offerings:
            courses = program_offering.program.courses.all()

            # Iterate over each course to accumulate session counts
            for course in courses:
                at_risk_students_new=get_no_of_at_risk_students_by_course(course=course)
                at_risk_students.update(at_risk_students_new)
               
        return at_risk_students

def get_no_of_at_risk_students_by_course(course):
    at_risk_students = set()
    course_offerings = course.course_offerings.all()

    for course_offering in course_offerings:
        
            at_risk_students_new=get_no_of_at_risk_students_by_course_offering(course_offering=course_offering)
            at_risk_students.update(at_risk_students_new)

    return at_risk_students

def get_no_of_at_risk_students_by_course_offering(course_offering):
    start_date,end_date=get_last_week_dates()
    # students only belong to course offering
    students = course_offering.student.all()
    # Initialize variable as tuple to avoid duplicate student track the count of at-risk students 
    
    # getting 100 query by this method 
    at_risk_students=get_at_risk_student_list_by_filter(start_date=start_date,end_date=end_date,students=students,course_offering=course_offering)
    
                

    # print("at Risk students ",at_risk_students)
    return at_risk_students

def get_no_of_at_risk_students_by_course_offerings(course_offerings):
    start_date,end_date=get_last_week_dates()
    # students only belong to course offering
    at_risk_students = set()
    for course_offering in course_offerings:
         
        students = course_offering.student.all()
        # Initialize variable as tuple to avoid duplicate student track the count of at-risk students 
        at_risk_students_new=get_at_risk_student_list_by_filter(start_date=start_date,end_date=end_date,students=students,course_offering=course_offering)
        at_risk_students.update(at_risk_students_new)

    # print("at Risk students ",at_risk_students)
    return at_risk_students

