from django.contrib import admin
from customUser.models import NewUser,Staff,Student
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from program.models import ProgramOffering,CourseOffering

# Register your models here.
# Extend the UserAdmin class
class CustomUserAdmin(UserAdmin):
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('gender', 'dob','address','phone','user_image')}),
    )
    list_display = ('id', 'get_full_name','username', 'email', 'dob', 'gender','phone','address','display_groups','user_image')  # Add 'get_full_name' to display combined name
    list_filter = UserAdmin.list_filter + ('gender',)  # Add 'position' and 'department' to filters
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


class StaffAdmin(admin.ModelAdmin):
    list_display=('id','staff','joining_date','designation','role','remark')


class ProgramOfferingInline(admin.StackedInline):
    model=Student.program_offering.through
    extra=1

class CourseOfferingInline(admin.StackedInline):
    model=Student.course_offering.through
    # model=CourseOffering
    extra=1



class StudentAdmin(admin.ModelAdmin):
    list_display=('id','student','joining_date','international_student','remark')
    inlines=[ProgramOfferingInline,CourseOfferingInline]

admin.site.register(Staff, StaffAdmin)  
admin.site.register(ProgramOffering)
admin.site.register(CourseOffering)
admin.site.register(Student,StudentAdmin)