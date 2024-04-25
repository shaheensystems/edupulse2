from django.contrib import admin
from base.models import Address,Campus
# Register your models here.


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id','unit_no','city', 'state', 'country','pin_code')  # Customize the displayed fields

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display=('id','name','address','get_student_enrollments','get_student_count')
    
    def get_student_enrollments(self,obj):
        student_enrollments=obj.calculate_total_student_enrolled()
        return len(student_enrollments)
    get_student_enrollments.short_description='Total Enrollments'
    
    def get_student_count(self,obj):
        student_enrollments=obj.calculate_total_student_enrolled()
        return len(set(student_enrollments))
    get_student_count.short_description='Total Students'
        