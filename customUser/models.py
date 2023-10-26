from django.db import models
from datetime import datetime
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel, Address,Campus
# Create your models here.

class NewUser(AbstractUser):
    Gender_Choice=[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
      
    ]
  
    gender=models.CharField(max_length=100,choices=Gender_Choice,null=True,blank=True)
    phone = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    dob=models.DateField( blank=True, null=True)
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    # address=models.CharField(max_length=255, verbose_name="Address")
    address=models.ForeignKey(Address, verbose_name="Address", on_delete=models.CASCADE,null=True,blank=True)
    campus=models.ForeignKey(Campus, verbose_name="Address", on_delete=models.CASCADE,null=True,blank=True)
    
    

class Staff(BaseModel):
    Designation_Choice=[
        ('Admin','Admin'),
        ('HR','Human Resources'),
        ('Lecturer','Lecturer'),
        ('Assistant Lecturer','Assistant Lecturer'),
        ('Consoler','Consoler'),
    ]
    staff=models.ForeignKey(NewUser,on_delete=models.CASCADE,null=True,blank=True)
    joining_date=models.DateField(null=True,blank=True)
    designation=models.CharField(max_length=255,choices=Designation_Choice,null=True,blank=True)
    role=models.CharField(max_length=255,null=True,blank=True)
    remark=models.TextField(max_length=1000,null=True,blank=True)

class Student(BaseModel):
    
    student=models.ForeignKey(NewUser,on_delete=models.CASCADE,null=True,blank=True)
    joining_date=models.DateField(null=True,blank=True) 
    international_student=models.BooleanField(default=False)
    remark=models.TextField(max_length=1000,null=True,blank=True)
    # course Offering 
    enrolled_course=models.CharField(max_length=255,null=True,blank=True)
