from django.db import models
from datetime import datetime
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel, Address,Campus
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from django.utils import timezone

from utils.function.helperAttendance import get_attendance_percentage_by_student
# Create your models here.

class Ethnicity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:

        verbose_name = 'Ethnicity'
        verbose_name_plural = 'Ethncitites'
    def __str__(self):
        return self.name




class NewUser(AbstractUser):
    Gender_Choice=[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),  
    ]  
    temp_id=models.CharField(max_length=255,blank=True,null=True)
    gender=models.CharField(max_length=100,choices=Gender_Choice,null=True,blank=True)
    phone = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    dob=models.DateField(default=None, blank=True, null=True)
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    nationality=models.CharField(max_length=255,null=True,blank=True)
    ethnicities = models.ManyToManyField(Ethnicity, blank=True, null=True)
    address=models.ForeignKey(Address, verbose_name="Address", on_delete=models.PROTECT,null=True,blank=True)
    
    campus=models.ForeignKey(Campus, verbose_name="Campus", on_delete=models.PROTECT,null=True,blank=True, related_name='users')
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    

class Staff(BaseModel):
    Designation_Choice=[
        ('Admin','Admin'),
        ('HR','Human Resources'),
        ('Lecturer','Lecturer'),
        ('Assistant Lecturer','Assistant Lecturer'),
        ('Counselor','Counselor'),
        ('Program Leader','Program Leader'),
        ('Head of School','Head of School'),

    ]
    staff = models.OneToOneField(NewUser, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    email_id=models.EmailField(null=True,blank=True)
    joining_date=models.DateField(null=True,blank=True)
    designation=models.CharField(max_length=255,choices=Designation_Choice,null=True,blank=True)
    role=models.CharField(max_length=255,null=True,blank=True)
    remark=models.TextField(max_length=1000,null=True,blank=True)
    class Meta:
        verbose_name = "Staff"  # Set the verbose name for the singular form
        verbose_name_plural = "Staff"

    def __str__(self):
        return f"{self.staff.gender} {self.email_id} {self.joining_date} {self.designation}"

class Student(BaseModel):
    
    student = models.OneToOneField(NewUser, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    joining_date=models.DateField(null=True,blank=True) 
    international_student=models.BooleanField(default=False)
    remark=models.TextField(max_length=1000,null=True,blank=True)
    # course Offering 
    enrolled_course=models.CharField(max_length=255,null=True,blank=True)
    email_id=models.EmailField(null=True,blank=True)
    enrollment_status=models.CharField(max_length=255,null=True,blank=True)
    passport_number=models.CharField(max_length=255,null=True,blank=True)
    visa_number=models.CharField(max_length=255,null=True,blank=True)
    visa_expiry_date=models.DateField(default=None, null=True,blank=True)

    def student_is_at_risk_for_last_week_status(self):
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)
        weekly_reports=self.weekly_reports.all()
        last_week_weekly_reports=weekly_reports.filter(
           sessions__attendance_date__range=[start_date_last_week, end_date_last_week] 
        )
       
        # print("last Week reports :",last_week_weekly_reports)
        
        for weekly_report in last_week_weekly_reports:

            if weekly_report.at_risk:
                # print(True)
                # print("student Id :",self.temp_id)
                # print("course name : ",weekly_report.course_offering)
                return True

    def calculate_attendance_percentage(self):
        return get_attendance_percentage_by_student(student=self)

    def __str__(self):
        return f"{self.student.temp_id} "


# table for enrolled courses for each course offering linked with each student for result , result status and attendance 