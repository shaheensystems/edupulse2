from django.db import models
from datetime import datetime
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel, Address,Campus
from django.contrib.auth.models import User
# Create your models here.

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
    address=models.ForeignKey(Address, verbose_name="Address", on_delete=models.CASCADE,null=True,blank=True)
    
    campus=models.ForeignKey(Campus, verbose_name="Campus", on_delete=models.CASCADE,null=True,blank=True, related_name='users')
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

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name}"


# table for enrolled courses for each course offering linked with each student for result , result status and attendance 