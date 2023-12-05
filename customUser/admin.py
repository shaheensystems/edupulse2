from django.contrib import admin
from customUser.models import NewUser,Staff,Student
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from report.models import Attendance

# Register your models here.
# Extend the UserAdmin class
class CustomUserAdmin(UserAdmin):
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('gender', 'dob','address','phone','user_image','campus')}),
    )
    list_display = ('id', 'get_full_name','username', 'email', 'dob', 'gender','phone','address','display_groups','user_image','campus')  # Add 'get_full_name' to display combined name
    list_filter = UserAdmin.list_filter + ('gender','campus',)  # Add 'position' and 'department' to filters
    readonly_fields=('last_login','date_joined')
    # Custom method to get combined first name and last name
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Full Name'  # Column header in admin

    def display_groups(self, obj):
        return format_html(', '.join([group.name for group in obj.groups.all()]))
    display_groups.short_description = 'Groups'  # Column header in admin

# Register the NewUser model with the custom admin class
admin.site.register(NewUser, CustomUserAdmin)





class ProgramOfferingInline(admin.StackedInline):
    model=Student.program_offering.through
    extra=1

class CourseOfferingInline(admin.StackedInline):
    model=Student.course_offerings.through
    # model=CourseOffering
    extra=1

class CourseOfferingStaffInline(admin.StackedInline):
    model=Staff.course_offerings.through
    # model=CourseOffering
    extra=1

class StaffAdmin(admin.ModelAdmin):
    list_display=('id','staff','joining_date','designation','role','remark')
    inlines=[CourseOfferingStaffInline]
    def get_courses_offered(self, obj):
        # courses_offered = obj.course_offering.through.objects.filter(student=obj)
        courses_offered = obj.course_offerings.all()
        # print("student name:",obj.student.first_name)
        # print( f"course name:", {str(course.course.name) for course in courses_offered})

        return ', '.join([str(course.course.name) for course in courses_offered])


    get_courses_offered.short_description = 'Courses Offered'

class StudentAdmin(admin.ModelAdmin):
    list_display=(
        'id','student','joining_date','international_student','remark',
        'enrolled_course','email_id','enrollment_status','passport_number',
        'visa_number','visa_expiry_date','get_programs_offered', 'get_courses_offered'
        )
    inlines=[ProgramOfferingInline,CourseOfferingInline]

    def get_programs_offered(self, obj):
        # print(obj.student.first_name)
        programs_offered = obj.program_offering.all()
        # print('program_offered:',programs_offered)

        # for program in programs_offered:
        #     print("prog object:",program.program.name)
    
        return ', '.join([str(program.program.name) for program in programs_offered])

    def get_courses_offered(self, obj):
        # courses_offered = obj.course_offering.through.objects.filter(student=obj)
        courses_offered = obj.course_offerings.all()
        # print("student name:",obj.student.first_name)
        # print( f"course name:", {str(course.course.name) for course in courses_offered})

        return ', '.join([str(course.course.name) for course in courses_offered])

    get_programs_offered.short_description = 'Programs Offered'
    get_courses_offered.short_description = 'Courses Offered'



admin.site.register(Staff, StaffAdmin)  

admin.site.register(Student,StudentAdmin)