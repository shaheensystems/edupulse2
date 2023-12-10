from report.models import WeeklyReport
from datetime import timedelta, datetime
from django.utils import timezone

def get_total_students_at_risk_by_course_offerings(course_offerings):
    at_risk_students = set()
    for course_offering in course_offerings:

        return at_risk_students.add(get_total_students_at_risk_by_course_offering(course_offering))

def get_total_students_at_risk_by_course_offering(course_offering):
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering
        students = course_offering.student.all()

        for student in students:
                    #  this on working fine total 4 result 
                    if student.temp_id=="2020792":
                        print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)
                        print("id Matched in CO M",student.temp_id)
                    # print("studnet :",student)
                    # Check if there is a weekly report for the student and course offering in the last week
                    weekly_report_last_week = WeeklyReport.objects.filter(
                        student=student,
                        course_offering=course_offering,
                        sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                    ).first()
                    # print("weekly report found ",weekly_report_last_week)
                    # If there is a weekly report, check if the student is at risk
                    if weekly_report_last_week and weekly_report_last_week.at_risk:
                        print("at _risk status on week report found CO M:",student.temp_id)
                        at_risk_students.add(student)
                        print("all object CO M",at_risk_students)

        return at_risk_students
        


def get_total_students_at_risk_by_program_offerings(program_offerings):
        # this function return a query set of unique students at risk  
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)

        # Initialize a set to track unique at-risk students
        at_risk_students = set()
        
        # Iterate over each program offering in the queryset
        for program_offering in program_offerings:
            # Get all students associated with the program offering
            courses=program_offering.program.course.all()
            
            for course in courses:
                course_offerings=course.course_offering.all()
                for course_offering in course_offerings:
                    students=course_offering.student.all()
                    # Iterate over each student to check their at-risk status for the last week
                    for student in students:
                        # Check if there is a weekly report for the student and program offering in the last week
                        weekly_reports_last_week = WeeklyReport.objects.filter(
                            student=student,
                            course_offering=course_offering,
                            sessions__attendance_date__range=[start_date_last_week, end_date_last_week],
                            at_risk=True
                        ).distinct()

                        # If there is a weekly report, add the student to the set
                        if weekly_reports_last_week.exists():
                            at_risk_students.add(student)

        return at_risk_students