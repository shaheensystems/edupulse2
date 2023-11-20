from django.contrib import admin
from program.models import Program, Course,ProgramOffering, CourseOffering
from customUser.models import Student
from report.models import WeeklyReport

from report.models import Attendance

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.course.through
    extra = 1  # Number of empty forms to display

class ProgramAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description']
    inlines = [CourseInline]

class CourseAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description','course_efts']

class ProgramOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','start_date','end_date','program')



class AttendanceInline(admin.TabularInline):
    model= Attendance
    extra =1
    
class WeeklyReportInline(admin.TabularInline):
    model=WeeklyReport
    extra=0

class CourseOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','start_date','end_date','course','result_status','result_status_code')
    inlines=[WeeklyReportInline,AttendanceInline]

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     # Get the CourseOffering instance
    #     course_offering = self.get_object(request, object_id)

    #     # Get the students enrolled in the CourseOffering
    #     students_enrolled = course_offering.student.all()

    #     print(students_enrolled)
    #     # Iterate through the students
    #     for student in students_enrolled:
    #         # Get the related attendance records for the current student
    #         attendance_records = Attendance.objects.filter(
    #             student=student,
    #             course_offering=course_offering
    #         )

    #         # Do something with the attendance records for each student
    #         for attendance_record in attendance_records:
    #             # You can access and process each attendance record here
    #             print(f"Student: {student}, Attended: {attendance_record.attended}")

    #     return super().change_view(request, object_id, form_url, extra_context)
    # def save_formset(self, request, form, formset, change):
    #     # Get the current user (assuming you're using Django's built-in User model)
    #     current_user = request.user
    #     print(current_user)
    #     # Iterate through the formset and set the "updated by" field
    #     for form in formset:
    #         if form.instance.pk is not None:
    #             form.instance.updated_by = current_user
    #             form.instance.created_by = current_user

    #     # Save the formset
    #     super().save_formset(request, form, formset, change)

admin.site.register(Program, ProgramAdmin)

admin.site.register(Course,CourseAdmin)
admin.site.register(ProgramOffering,ProgramOfferingAdmin)
admin.site.register(CourseOffering,CourseOfferingAdmin)
