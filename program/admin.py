from django.contrib import admin
from .models import Program, Course,ProgramOffering

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.course.through
    extra = 1  # Number of empty forms to display

class ProgramAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description']
    inlines = [CourseInline]

class CourseAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description','course_efts']

admin.site.register(Program, ProgramAdmin)

admin.site.register(Course,CourseAdmin)
