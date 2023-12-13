from django.db import models
from base.models import BaseModel
from customUser.models import Student, Staff
from datetime import timedelta, datetime
from django.utils import timezone

from utils.function.helperAttendance import get_attendance_percentage,get_attendance_percentage_by_program,get_attendance_percentage_by_course,get_attendance_percentage_by_program_offering,get_attendance_percentage_by_course_offering


from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_course_offering,get_no_of_at_risk_students_by_program_offering,get_no_of_at_risk_students_by_course,get_no_of_at_risk_students_by_program



class Program(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    
    def calculate_attendance_percentage(self):
        return get_attendance_percentage_by_program(program=self,total_sessions=0,present_sessions=0)
  
    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_program(program=self)
        
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
        return get_no_of_at_risk_students_by_course(course=self)
    
    def calculate_attendance_percentage(self):
        return get_attendance_percentage_by_course(course=self,total_sessions=0,present_sessions=0)
    
    def __str__(self):
        return f'{self.temp_id}-{self.name}'


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
        return get_attendance_percentage_by_course_offering(course_offering=self,total_sessions=0,present_sessions=0)
     
    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_course_offering(course_offering=self)

        
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
        return get_attendance_percentage_by_program_offering(program_offering=self,total_sessions=0,present_sessions=0)

    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_program_offering(program_offering=self)
        

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


   
    