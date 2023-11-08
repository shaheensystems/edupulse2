from django.db import models
from base.models import BaseModel
from customUser.models import Student  # Import the Student model
from program.models import ProgramOffering, CourseOffering,Course
from django.utils import timezone
from django.db import models

class Attendance(BaseModel):
    # this table can be access by teacher for each course and each student to mark attendance
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE, null=True, blank=True)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, null=True, blank=True)  
    is_present = models.BooleanField(default=False, null=True, blank=True)  
    attendance_date = models.DateField(default=timezone.now, null=True, blank=True)
    remark=models.TextField(null=True,blank=True,max_length=255)

    class Meta:
        unique_together = ('student', 'program_offering', 'course_offering')

    def __srt__(self):
        return f"{self.student} - {self.course_offering} - {self.attendance_date}-{self.is_present}"

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
