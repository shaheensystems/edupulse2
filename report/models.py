from django.db import models
from base.models import BaseModel
from customUser.models import Student  # Import the Student model
from program.models import ProgramOffering, CourseOffering
from django.utils import timezone
from django.db import models
from datetime import date
from django.db.models import Count, F



from utils.function.BaseValues_List import ATTENDANCE_CHOICE, ENGAGEMENT_CHOICE, ACTION_CHOICE, FOLLOW_UP_CHOICE, PERFORMANCE_CHOICE, ASSESSMENT_CHOICE


    
    
class Attendance(BaseModel):
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True,related_name='attendances')
    
    # program offering will not connect with attendance
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE, null=True, blank=True,related_name='attendances')
    
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, null=True, blank=True ,related_name="attendances")  
    is_present = models.CharField(max_length=255,choices=ATTENDANCE_CHOICE,default="present", null=True, blank=True)  
    attendance_date = models.DateField(default=timezone.now, null=True, blank=True)
    remark=models.TextField(null=True,blank=True,max_length=255)
    weekly_reports = models.ManyToManyField('WeeklyReport', related_name='attendances')
    
    # new attributes 
    week_no=models.PositiveIntegerField()
    session_no=models.PositiveIntegerField()

   
    
    class Meta:
        unique_together = ('student', 'course_offering','attendance_date','week_no','session_no')

    def __srt__(self):
        return f"{self.student} - {self.course_offering} - {self.attendance_date}-{self.is_present}"

class WeeklyReport(BaseModel):
    # ENGAGEMENT_CHOICE=[
    #     ('na','N/A'),
    #     ('on track canvas','On Track - CANVAS'),
    #     ('on track assessment','On Track - Assessment'),
    #     ('on track learning activity','On Track - Learning Activity'),
    #     ('on track blended','On Track - Blended'),
    #     ('not engaged','Not Engaged'),
    # ]
    # ACTION_CHOICE=[
    #     ('na','N/A'),
    #     ('follow up email and call','Follow Up Email and Call'),
    #     ('pastoral care','Pastoral Care'),
    #     ('personalized study plan/Extra session','Personalized Study Plan /Extra Session'),
    #     ('emergency contact','Emergency Contact'),
    #     ('other','Other'),
    # ]
    # FOLLOW_UP_CHOICE=[
    #     ('na','N/A'),
    #     ('warning letter 1','Warning Letter 1'),
    #     ('warning letter 2','Warning Letter 2'),
    # ]
    # PERFORMANCE_CHOICE=[
    #     ('na','N/A'),
    #     ('poor','POOR'),
    #     ('good','GOOD'),
    #     ('moderate','MODERATE'),
    # ]
    # ASSESSMENT_CHOICE=[
    #     ('na','N/A'),
    #     ('making progress','MAKING PROGRESS '),
    #     ('no progress','NO PROGRESS'),
    #     ('request extension','REQUEST EXTENSION'),
    #     ('submitted','SUBMITTED'),
    #     ('not submitted','NOT SUBMITTED'),
    #     ('failed','FAILED'),
    #     ('re-sit','RE-SIT'),
    # ]
    
    
    week_number=models.PositiveIntegerField(blank=True,null=True)
    # sessions will be list of all attendance in one week
    sessions=models.ManyToManyField(Attendance, verbose_name=("sessions"))
    engagement=models.CharField(choices=ENGAGEMENT_CHOICE,default="na",null=True,blank=True, max_length=255)
    action=models.CharField(choices=ACTION_CHOICE,null=True,blank=True, max_length=255,default='na')
    follow_up=models.CharField(choices=FOLLOW_UP_CHOICE,null=True,blank=True, max_length=255,default="na")
    course_offering=models.ForeignKey(CourseOffering, verbose_name=("Course Offering"), on_delete=models.CASCADE,null=True, blank=True ,related_name='weekly_reports')
    student=models.ForeignKey(Student, verbose_name=("Student"), on_delete=models.CASCADE,related_name='weekly_reports')
    no_of_pages_viewed_on_canvas=models.PositiveIntegerField(null=True,blank=True, default=0)
    login_in_on_canvas=models.BooleanField(default=False, blank=True,null=True)
    # at_risk Status
    assessment_status=models.CharField( choices=ASSESSMENT_CHOICE, max_length=255,null=True,blank=True,default="n/a")
    at_risk=models.BooleanField(default=False,null=True,blank=True)
    
    def get_week_number(self):
        start_date=self.course_offering.start_date
        end_date=self.course_offering.end_date
        
        attendance_dates = [session.attendance_date for session in self.sessions.all()]

        # Find the minimum attendance date
        min_attendance_date = min(attendance_dates) if attendance_dates else date.today()  # Use today's date if there are no attendance dates
        # Calculate the number of weeks between start_date and min_attendance_date
        num_weeks = (min_attendance_date - start_date).days // 7 + 1
        
        return num_weeks
        
        






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


class StudentEnrollment(BaseModel):
    RESULT_CHOICE=[
        ('awaited','Awaited'),
        ('pass','Pass'),
        ('fail','Fail'),
        ('dropped','Dropped'),
    ]
    student=models.ForeignKey(Student, verbose_name='student', on_delete=models.CASCADE,related_name='student_enrollments')
    course_offering=models.ForeignKey(CourseOffering, verbose_name='course_offering', on_delete=models.CASCADE,related_name='student_enrollments')
    program_offering=models.ForeignKey(ProgramOffering, verbose_name='program_offering', on_delete=models.CASCADE,related_name='student_enrollments')
    status=models.BooleanField(default=True)
    result=models.CharField(choices=RESULT_CHOICE,null=True,blank=True, max_length=255,default='awaited')
    
    