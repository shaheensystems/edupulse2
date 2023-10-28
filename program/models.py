from django.db import models
from base.models import BaseModel
from customUser.models import Student

# Create your models here.
# class YearlyTerm(BaseModel):
#     year=models.DateField(blank=True, null=True)
#     start_date=models.DateField(blank=True,null=True)
#     end_date=models.DateField(blank=True,null=True)

# class SemesterTerm(BaseModel):
#     year=models.DateField(blank=True, null=True)
#     s1_start_date=models.DateField(blank=True,null=True)
#     s1_end_date=models.DateField(blank=True,null=True)
#     s2_start_date=models.DateField(blank=True,null=True)
#     s2_end_date=models.DateField(blank=True,null=True)

# class Term(BaseModel):
#     Term_Type=[
#         ('yearly','Yearly'),
#         ('monthly','monthly'),
#         ('quarterly','Quarterly'),
#         ('trimester','Trimester'),
#         ('semester','Semester'),
#         ('manual','Manual'),
#     ]
#     year=models.DateField(null=True,blank=True)
#     term_type=models.CharField(max_length=255,choices=Term_Type, blank=True, null=True)

class Program(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    

class Course(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    program = models.ManyToManyField(Program, blank=True, related_name='course')

class CourseOffering(BaseModel):
    course=models.ForeignKey(Course, verbose_name=("course"), on_delete=models.CASCADE)
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)
    student = models.ManyToManyField(Student, blank=True, related_name='course_offering')

class ProgramOffering(BaseModel):
    program=models.ForeignKey(Program, verbose_name=("program"), on_delete=models.CASCADE)
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)
    student=models.ManyToManyField(Student,blank=True,related_name='program_offering')


   
    