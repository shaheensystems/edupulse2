from django.shortcuts import render
from django.db.models import Count,Q
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
# Create your views here.

class CourseListView(ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='course'

class CourseDetailView(DetailView):
    model=Course
    template_name='program/course/course_detail.html'
    context_object_name='course'



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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Assuming 'performance' is a field in the WeeklyReport model
        courses = self.object.program.course.all()  # Adjust the related name accordingly
        # print("All course",courses)
        # Dictionary to store poor performance count for each course
        poor_performance_data = []

        for course in courses:
            # print("Each Course",course)
            print("for each course get all course_offering :",course.course_offering.all().count())
            for course_offering in course.course_offering.all():
                weekly_reports = course_offering.weekly_reports.values('week_number').annotate(
                total=Count('pk'),
                poor_performance=Count('pk', filter=Q(performance='poor'))
                )

                for report in weekly_reports:
                    week_number = report['week_number']
                    total_count = report['total']
                    poor_count = report['poor_performance']

                     # Create a dictionary for each course offering and week
                    offering_data = {
                    'course_offering': course_offering,
                    'week_number': week_number,
                    'total_students': total_count,
                    'poor_performance_count': poor_count,
                    }

                    poor_performance_data.append(offering_data)

        context['poor_performance_data'] = poor_performance_data
        context['total_course_offering_count']=course.course_offering.all().count()
        return context

class CourseOfferingListView(ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offering'

class CourseOfferingDetailView(DetailView):
    model = CourseOffering
    template_name = 'program/course/course_offering_detail.html'  
    context_object_name = 'course_offering'  
