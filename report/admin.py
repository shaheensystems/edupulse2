from django.contrib import admin
from report.models import Attendance, CourseResult

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'program_offering', 'course_offering', 'is_present', 'attendance_date')
    list_filter = ('student', 'program_offering', 'course_offering', 'is_present', 'attendance_date')
    search_fields = ('student__student__first_name', 'student__student__last_name', 'program_offering__program__name', 'course__name')
    
    # Customize the admin change form for the 'Attendance' model if needed
    fieldsets = (
        ('Attendance Information', {
            'fields': ('student', 'program_offering', 'course_offering', 'is_present', 'attendance_date')
        }),
    )

admin.site.register(Attendance, AttendanceAdmin)

class CourseResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'program_offering', 'course_offering', 'marks', 'result_status')
    list_filter = ('student', 'program_offering', 'course_offering')
    search_fields = ('student__student__username', 'program_offering__program__name', 'course_offering__name')
    list_per_page = 20

admin.site.register(CourseResult, CourseResultAdmin)