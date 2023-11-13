from django.db import models
from base.models import BaseModel
from customUser.models import Student  # Import the Student model
from program.models import ProgramOffering, CourseOffering,Course
from django.utils import timezone
from django.db import models

class Attendance(BaseModel):
    ATTENDANCE_CHOICE=[
        ('present','Present'),
        ('absent','Absent'),
        ('informed absent','Informed Absent'),
        ('tardy','Tardy'),
    ]
    # this table can be access by teacher for each course and each student to mark attendance
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE, null=True, blank=True)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, null=True, blank=True)  
    is_present = models.CharField(max_length=255,choices=ATTENDANCE_CHOICE,default="present", null=True, blank=True)  
    attendance_date = models.DateField(default=timezone.now, null=True, blank=True)
    remark=models.TextField(null=True,blank=True,max_length=255)

    class Meta:
        unique_together = ('student', 'program_offering', 'course_offering')

    def __srt__(self):
        return f"{self.student} - {self.course_offering} - {self.attendance_date}-{self.is_present}"

class WeeklyReport(BaseModel):
    ENGAGEMENT_CHOICE=[
        ('na','N/A'),
        ('on track canvas','On Track - CANVAS'),
        ('on track assessment','On Track - Assessment'),
        ('on track learning activity','On Track - Learning Activity'),
        ('on track blended','On Track - Blended'),
        ('not engaged','Not Engaged'),
    ]
    ACTION_CHOICE=[
        ('na','N/A'),
        ('follow up email and call','Follow Up Email and Call'),
        ('pastoral care','Pastoral Care'),
        ('personalised study plan/Extra session','Personlaised Study Plan /Extra Session'),
        ('emergency contact','Emergency Contact'),
        ('other','Other'),
    ]
    FOLLOW_UP_CHOICE=[
        ('na','N/A'),
        ('warning letter 1','Warning Letter 1'),
        ('warning letter 2','Warning Letter 2'),
    ]
    week_number=models.PositiveIntegerField(blank=True,null=True)
    # sessions will be list of all attendance in one week
    sessions=models.ManyToManyField(Attendance, verbose_name=("sessions"))
    engagement=models.CharField(choices=ENGAGEMENT_CHOICE,default="n/a",null=True,blank=True, max_length=255)
    action=models.CharField(choices=ACTION_CHOICE,null=True,blank=True, max_length=255,default='n/a')
    follow_up=models.CharField(choices=FOLLOW_UP_CHOICE,null=True,blank=True, max_length=255,default="n/a")
    course_offering=models.ForeignKey(CourseOffering, verbose_name=("Course Offering"), on_delete=models.CASCADE,related_name='weekly_reports')
    student=models.ForeignKey(Student, verbose_name=("Student"), on_delete=models.CASCADE,related_name='weekly_reports')

class CourseResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE, null=True, blank=True)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE)
    result_status_code=models.CharField(max_length=255,null=True,blank=True)
    result_status=models.CharField(max_length=255,null=True,blank=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    result_status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.program_offering} - {self.course_offering}"

    class Meta:
        unique_together = ('student', 'program_offering', 'course_offering')
