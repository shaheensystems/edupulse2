from django.contrib import admin
from .models import Program, Course,ProgramOffering

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.course.through
    extra = 1  # Number of empty forms to display

class ProgramAdmin(admin.ModelAdmin):
    list_display=['id','temp_id','name','description']
    inlines = [CourseInline]

admin.site.register(Program, ProgramAdmin)
admin.site.register(Course)
