from django.db import models
from base.models import BaseModel
from customUser.models import Student  # Import the Student model
from program.models import ProgramOffering, Course
from django.utils import timezone

class Attendance(BaseModel):
    # this table can be access by teacher for each course and each student to mark attendance
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  
    attended = models.BooleanField(default=False)  
    attendance_date = models.DateField(default=timezone.now, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'program_offering', 'course')

from django.db import models

class CourseResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    program_offering = models.ForeignKey(ProgramOffering, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    result_status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.program_offering} - {self.course}"

    class Meta:
        unique_together = ('student', 'program_offering', 'course')
