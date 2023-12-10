from django.db import models
from base.models import BaseModel
from customUser.models import Student, Staff
from datetime import timedelta, datetime
from django.utils import timezone





class Program(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    
    
    def calculate_attendance_percentage(self):
       
        # Get all the courses associated with the program
        courses = self.course.all()
        # print("all courses linked with program_offering :",courses)
        # Initialize variables to track total and present sessions
        total_sessions = 0
        present_sessions = 0

        # Iterate over each course to accumulate session counts
        for course in courses:
            # Get the CourseOffering associated with the current course and program offering
            try:
                course_offerings = CourseOffering.objects.filter(course=course)
                # print("get all course_offering linked is course:",course_offerings)
            except CourseOffering.DoesNotExist:
                # Handle the case where there is no associated CourseOffering for the current course and program offering
                continue
            
            if course_offerings:
                for course_offering in course_offerings:
                    total_sessions+=course_offering.attendance.count()
                    present_sessions += course_offering.attendance.filter(is_present='present').count()
                    # print("total attendance sessions:",total_sessions)
                    # print("total present attendance sessions:",present_sessions)
            

        # Check if there are any sessions before calculating the percentage to avoid division by zero
        if total_sessions > 0:
            # Calculate the attendance percentage as (present_sessions / total_sessions) * 100
            attendance_percentage = (present_sessions / total_sessions) * 100

            # Round the percentage to two decimal places for better readability
            return round(attendance_percentage, 2)

        # If there are no sessions, return 0.0 as the default attendance percentage
        return 0.0
    
    def calculate_no_at_risk_student_for_last_week(self):
        program=self
        # print("all program offering from model ",program_offerings)
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        # Get all courses associated with the program
        courses = program.course.all()

        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering
        # print("count students :",students.count())
        # Iterate over each course to accumulate session counts
        for course in courses:
            # Get all CourseOfferings associated with the current course and program offering
            course_offerings = course.course_offering.all()

            # Iterate over each CourseOffering to handle potential multiple objects
            for course_offering in course_offerings:
                students=course_offering.student.all()
               
                # Iterate over each student to check their at-risk status for the last week
                for student in students:
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
                        # print("at _risk status on week report found PO M",student.temp_id)
                        at_risk_students.add(student)
                        # print("all object PO M",at_risk_students)

        return at_risk_students
    
    def __str__(self):
        return f'{self.temp_id}-{self.name}'

class Course(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    program = models.ManyToManyField(Program, blank=True, related_name='course')
    course_efts=models.FloatField(null=True,blank=True)

    def calculate_no_at_risk_student_for_last_week(self):
        course=self
        # print("all program offering from model ",program_offerings)
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)


        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering
        # print("count students :",students.count())
        # Iterate over each course to accumulate session counts
         # Get all CourseOfferings associated with the current course and program offering
        course_offerings = course.course_offering.all()

        # Iterate over each CourseOffering to handle potential multiple objects
        for course_offering in course_offerings:
            students=course_offering.student.all()
            
            # Iterate over each student to check their at-risk status for the last week
            for student in students:
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
                    # print("at _risk status on week report found PO M",student.temp_id)
                    at_risk_students.add(student)
                    # print("all object PO M",at_risk_students)

        return at_risk_students
    
    def __str__(self):
        return f'{self.temp_id}-{self.name}'
   
    def calculate_attendance_percentage(self):
        total_sessions = 0
        present_sessions = 0
        course_offerings=self.course_offering.all()
        for course_offering in course_offerings:
            total_sessions+=course_offering.attendance.count()
            present_sessions += course_offering.attendance.filter(is_present='present').count()
        if total_sessions > 0:
            # Calculate the attendance percentage as (present_sessions / total_sessions) * 100
            attendance_percentage = (present_sessions / total_sessions) * 100

            # Round the percentage to two decimal places for better readability
            return round(attendance_percentage, 2)

        # If there are no sessions, return 0.0 as the default attendance percentage
        return 0.0



class CourseOffering(BaseModel):
    OFFERING_CHOICES = [
        ('online', 'ONLINE'),
        ('offline', 'OFFLINE'),
        ('blended', 'BLENDED'),
    ]

    course=models.ForeignKey(Course, verbose_name=("course"), on_delete=models.CASCADE,null=True,blank=True,related_name='course_offering')
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)

    # both field below has to go with student or linked with result table with each student with each course offering
    result_status_code=models.CharField(max_length=255,null=True,blank=True)
    result_status=models.CharField(max_length=255,null=True,blank=True)

    student = models.ManyToManyField(Student,blank=True ,related_name='course_offerings')
    teacher = models.ManyToManyField(Staff,blank=True ,related_name='course_offerings')
    offering_mode = models.CharField(max_length=10,choices=OFFERING_CHOICES,default='online',blank=True, null=True,help_text='Select the mode of course offering: Online, Offline, or Blended'
    )
    

    def calculate_attendance_percentage(self):
        
        total_sessions=self.attendance.count()
        present_sessions = self.attendance.filter(is_present='present').count()
        if total_sessions > 0:
            # Calculate the attendance percentage as (present_sessions / total_sessions) * 100
            attendance_percentage = (present_sessions / total_sessions) * 100

            # Round the percentage to two decimal places for better readability
            return round(attendance_percentage, 2)

        # If there are no sessions, return 0.0 as the default attendance percentage
        return 0.0
    #  this code working  fine total 4 result  
    def calculate_no_at_risk_student_for_last_week(self):
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        students = self.student.all()

        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering
        students = self.student.all()

        for student in students:
                    #  this on working fine total 4 result 
                    # if student.temp_id=="2020792":
                    #     print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)
                    #     print("id Matched in CO M",student.temp_id)
                    # print("student :",student)
                    # Check if there is a weekly report for the student and course offering in the last week
                    weekly_report_last_week = WeeklyReport.objects.filter(
                        student=student,
                        course_offering=self,
                        sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                    ).first()
                    # print("weekly report found ",weekly_report_last_week)
                    # If there is a weekly report, check if the student is at risk
                    if weekly_report_last_week and weekly_report_last_week.at_risk:
                        # print("at _risk status on week report found CO M:",student.temp_id)
                        at_risk_students.add(student)
                        # print("all object CO M",at_risk_students)

        return at_risk_students
        
    def get_all_students(self):
        students = self.student.all()
        # print("Students from Program Offering:", students)
        return students
    
    def __str__(self):
        return f'{self.temp_id}-{self.course.name}'

class ProgramOffering(BaseModel):
    program=models.ForeignKey(Program, verbose_name=("program"), on_delete=models.CASCADE,null=True,blank=True,related_name="program_offerings")
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)
    program_leader=models.ManyToManyField(Staff,blank=True ,null=True,related_name='program_offerings')
    student=models.ManyToManyField(Student,blank=True,related_name='program_offering')

    def calculate_attendance_percentage(self):
       
        # Get all the courses associated with the program
        courses = self.program.course.all()
        # print("all courses linked with program_offering :",courses)
        # Initialize variables to track total and present sessions
        total_sessions = 0
        present_sessions = 0

        # Iterate over each course to accumulate session counts
        for course in courses:
            # Get the CourseOffering associated with the current course and program offering
            try:
                course_offerings = CourseOffering.objects.filter(course=course)
                # print("get all course_offering linked is course:",course_offerings)
            except CourseOffering.DoesNotExist:
                # Handle the case where there is no associated CourseOffering for the current course and program offering
                continue
            
            if course_offerings:
                for course_offering in course_offerings:
                    total_sessions+=course_offering.attendance.count()
                    present_sessions += course_offering.attendance.filter(is_present='present').count()
                    # print("total attendance sessions:",total_sessions)
                    # print("total present attendance sessions:",present_sessions)
            

        # Check if there are any sessions before calculating the percentage to avoid division by zero
        if total_sessions > 0:
            # Calculate the attendance percentage as (present_sessions / total_sessions) * 100
            attendance_percentage = (present_sessions / total_sessions) * 100

            # Round the percentage to two decimal places for better readability
            return round(attendance_percentage, 2)

        # If there are no sessions, return 0.0 as the default attendance percentage
        return 0.0
    # wrong code total 2 result , 4 result are correct


    # at_risk_student_for_last_week=get_total_students_at_risk_by_program_offerings(self.objects.all())


    def calculate_no_at_risk_student_for_last_week(self):
        # program_offerings=self
        # print("all program offering from model ",program_offerings)
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        # Get all courses associated with the program
        courses = self.program.course.all()

        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering
        # print("count students :",students.count())
        # Iterate over each course to accumulate session counts
        for course in courses:
            # Get all CourseOfferings associated with the current course and program offering
            course_offerings = course.course_offering.all()

            # Iterate over each CourseOffering to handle potential multiple objects
            for course_offering in course_offerings:
                students=course_offering.student.all()
               
                # Iterate over each student to check their at-risk status for the last week
                for student in students:
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
                        # print("at _risk status on week report found PO M",student.temp_id)
                        at_risk_students.add(student)
                        # print("all object PO M",at_risk_students)

        return at_risk_students

    def list_course_offerings(self):
        courses = self.program.course.all()
        course_offerings_list = []
        # Iterate over each course to collect course offerings
        for course in courses:
            # Get the course offerings associated with the current course
            course_offerings = CourseOffering.objects.filter(course=course)

            # Extend the list with the course offerings
            course_offerings_list.extend(course_offerings)

        return course_offerings_list
    
    def get_all_students(self):
        students = self.student.all()
        # print("Students from Program Offering:", students)
        return students

    def __str__(self):
        return f'{self.temp_id}-{self.program.name}'


   
    