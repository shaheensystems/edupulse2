from django.contrib import admin
from report.models import Attendance, CourseResult, WeeklyReport,StudentEnrollment

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

class SessionsInline(admin.TabularInline):  # You can also use admin.StackedInline for a different layout
    model = WeeklyReport.sessions.through  # Use the through attribute to access the Attendance model
    extra = 1  # Number of empty forms to display


class WeeklyReportAdmin(admin.ModelAdmin):
    list_display=('week_number','get_attendance_date','engagement','action','follow_up','course_offering','student','get_sessions_is_present','no_of_pages_viewed_on_canvas','login_in_on_canvas','assessment_status','at_risk')
    inlines = [SessionsInline]
    
    def get_sessions_is_present(self, obj):
        return ', '.join(session.is_present for session in obj.sessions.all())

    get_sessions_is_present.short_description = 'Sessions is_present'

    def get_attendance_date(self, obj):
        return ', '.join(str(session.attendance_date) for session in obj.sessions.all())
    
    get_attendance_date.short_description="Attendance Date"

admin.site.register(WeeklyReport, WeeklyReportAdmin)

class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display=('student','course_offering','program_offering','status','result')

admin.site.register(StudentEnrollment,StudentEnrollmentAdmin)