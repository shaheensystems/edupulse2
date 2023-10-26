from django.contrib import admin
from .models import Program, Course,ProgramOffering

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.courses.through
    extra = 1  # Number of empty forms to display

class ProgramAdmin(admin.ModelAdmin):
    inlines = [CourseInline]

admin.site.register(Program, ProgramAdmin)
admin.site.register(Course)
