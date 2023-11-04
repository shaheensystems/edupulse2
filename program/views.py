from django.shortcuts import render
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
# Create your views here.

class CourseListView(ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='course'
class CourseOfferingListView(ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offering'

class ProgramListView(ListView):
    model=Program
    template_name='program/program/program_list.html'
    context_object_name='programs'

class ProgramDetailView(DetailView):
    model=Program
    template_name='program/program/program_detail.html'
    context_object_name='program'

class ProgramOfferingListView(ListView):
    model=ProgramOffering
    template_name='program/program/program_offering_list.html'
    context_object_name='program_offering'

class ProgramOfferingDetailView(DetailView):
    model = ProgramOffering
    template_name = 'program/program/program_offering_detail.html'  
    context_object_name = 'program_offering'  
