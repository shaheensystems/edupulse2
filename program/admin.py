from django.contrib import admin
from program.models import Program, Course,ProgramOffering, CourseOffering
from customUser.models import Student
from report.models import WeeklyReport

from report.models import Attendance

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.course.through
    extra = 1  # Number of empty forms to display

class ProgramAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description','calculate_total_no_of_student','calculate_attendance_percentage','calculate_no_at_risk_student_for_last_week']
    inlines = [CourseInline]
    def calculate_attendance_percentage(self, obj):
        return obj.calculate_attendance_percentage()

    calculate_attendance_percentage.short_description = 'Attendance Percentage'

    def calculate_no_at_risk_student_for_last_week(self, obj):
        return len(obj.calculate_no_at_risk_student_for_last_week())

    calculate_no_at_risk_student_for_last_week.short_description = 'No. of At-Risk Students (Last Week)'

    def calculate_total_no_of_student(self,obj):
        return len( obj.calculate_total_no_of_student())
    
    calculate_total_no_of_student.short_description = 'No. of  Students'

class CourseAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','calculate_total_no_of_student','description','course_efts']
    
    def calculate_total_no_of_student(self,obj):
        return len(obj.calculate_total_no_of_student())
    
    calculate_total_no_of_student.short_description = 'No. of  Students'

class ProgramOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','offering_mode','start_date','end_date','calculate_total_no_of_student','get_all_students','program')

    def calculate_total_no_of_student(self,obj):
        return obj.calculate_total_no_of_student()
    calculate_total_no_of_student.short_description = 'No. of  Students'

    def get_all_students(self,obj):
        return obj.get_all_students().count()
    get_all_students.short_description = 'No. of  Students(D)'



class AttendanceInline(admin.TabularInline):
    model= Attendance
    extra =1
    
class WeeklyReportInline(admin.TabularInline):
    model=WeeklyReport
    extra=0

class CourseOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','offering_mode','start_date','end_date','calculate_total_no_of_student','get_all_students','course','result_status','result_status_code')
    # inlines=[WeeklyReportInline,AttendanceInline]

    def calculate_total_no_of_student(self,obj):
        return obj.calculate_total_no_of_student()
    
    calculate_total_no_of_student.short_description = 'No. of  Students Incorrect method '

    def get_all_students(self,obj):
        return obj.get_all_students().count()
    get_all_students.short_description = 'No. of  Students(D)'


admin.site.register(Program, ProgramAdmin)

admin.site.register(Course,CourseAdmin)
admin.site.register(ProgramOffering,ProgramOfferingAdmin)
admin.site.register(CourseOffering,CourseOfferingAdmin)
