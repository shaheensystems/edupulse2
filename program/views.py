from django.shortcuts import render
from django.db.models import Count,Q
from customUser.models import Staff
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class CourseListView(LoginRequiredMixin,ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='course'

class CourseDetailView(LoginRequiredMixin,DetailView):
    model=Course
    template_name='program/course/course_detail.html'
    context_object_name='course'



class ProgramListView(LoginRequiredMixin,ListView):
    model=Program
    template_name='program/program/program_list.html'
    context_object_name='programs'

class ProgramDetailView(LoginRequiredMixin,DetailView):
    model=Program
    template_name='program/program/program_detail.html'
    context_object_name='program'

class ProgramOfferingListView(LoginRequiredMixin,ListView):
    model=ProgramOffering
    template_name='program/program/program_offering_list.html'
    context_object_name='program_offering'

class ProgramOfferingDetailView(LoginRequiredMixin,DetailView):
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
                # poor_performance=Count('pk', filter=Q(performance='poor'))
                )

                for report in weekly_reports:
                    week_number = report['week_number']
                    total_count = report['total']
                    # poor_count = report['poor_performance']

                     # Create a dictionary for each course offering and week
                    offering_data = {
                    'course_offering': course_offering,
                    'week_number': week_number,
                    'total_students': total_count,
                    # 'poor_performance_count': poor_count,
                    }

                    # poor_performance_data.append(offering_data)

        # context['poor_performance_data'] = poor_performance_data
        context['total_course_offering_count']=course.course_offering.all().count()
        return context

class CourseOfferingListView(LoginRequiredMixin,ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offerings'
    
    print("initialise Course Offering view ")
    def get_queryset(self):
        user = self.request.user
        print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists():
            print("condition matched admin")
            return CourseOffering.objects.all()

        # Check if the user is a teacher
        elif user.groups.filter(name='Teacher').exists():
            print("condition matched for teacher")
            # Assuming there is a ForeignKey from CourseOffering to Teacher model
            # only course offering where teacher is equal to current user
            return CourseOffering.objects.filter(teacher__staff=user)
        elif user.groups.filter(name='Student').exists():
            return CourseOffering.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return CourseOffering.objects.none()
    print(context_object_name)
    

class CourseOfferingDetailView(LoginRequiredMixin,DetailView):
    model = CourseOffering
    template_name = 'program/course/course_offering_detail.html'  
    context_object_name = 'course_offering'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = 'table'  # Add the 'view' context value list or detail or table

        all_attendance=context['course_offering'].attendance.all()
        # Create a dictionary to store attendance count date-wise
        attendance_count = {}

        # Iterate through each attendance record
        for attendance in all_attendance:
            # Get the attendance date
            date = attendance.attendance_date
            print("Date :",date)

            # If the date is not in the dictionary, add it
            if date not in attendance_count:
                attendance_count[date] = 0

            # Update the attendance count based on the 'is_present' value
            if attendance.is_present == 'present':
                attendance_count[date] += 1
    
        # Extract the labels and data for the chart
        labels = list(attendance_count.keys())
        data = list(attendance_count.values())

        formatted_labels = [date.strftime("%Y-%m-%d") for date in labels]
        # set initial value 0 and empty to get a good chart view 
        formatted_labels.insert(0, "")
        data.insert(0, 0)   
        print("labels :",formatted_labels)       

        # Add the labels and data to the context
        context['chart_data_attendance'] = {
            'labels': formatted_labels,
            'data': data,
        }

        print("All attendance:",all_attendance)
        return context
   


