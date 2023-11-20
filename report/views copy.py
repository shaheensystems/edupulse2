from django.shortcuts import render
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from report.models import Attendance
from report.form import AttendanceForm
from django.shortcuts import get_object_or_404
from program.models import CourseOffering
from django.urls import reverse
from django.forms import modelformset_factory
# from customUser.models import Student
# Create your views here.

class AttendanceListView(ListView):
    model=Attendance
    template_name='report/attendance/attendance_list.py'
    context_object_name='attendance'

class AttendanceCreateView(CreateView):
    model=Attendance
    template_name='report/attendance/attendance_form.py'
    form_class=AttendanceForm
    field=['student','program_offering','course_offering','is_present','attendance_date','attendance_date']
    # success_url= reverse('program_offering_list') 
    def get_success_url(self):
        # Capture the previous URL from the HTTP_REFERER header
        previous_url = self.request.META.get('HTTP_REFERER', '')
        
        # You can add additional checks to ensure the previous URL is within your domain
        # to prevent external redirection.

        # You may also want to add logic to handle the case when the previous URL is not available.
        if previous_url:
            return previous_url

        # If the previous URL is not available, you can specify a default URL to redirect to.
        # For example, you can use reverse() to specify a URL name.
        return reverse('program_offering_list')
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # You need to add code to get the course offering here, assuming you have a method or logic for that
    #     course_offering = get_object_or_404(CourseOffering, pk=self.kwargs['pk'])
    #     context['course_offering'] = course_offering
    #      # Create a form instance for each student in the course_offering
    #     student_forms = []
    #     for student in course_offering.student.all():
    #         student_form = self.form_class(initial={'student': student, 'course_offering': course_offering})
    #         student_forms.append(student_form)
        
    #     context['student_forms'] = student_forms
    #     return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # You need to add code to get the course offering here, assuming you have a method or logic for that
        course_offering = get_object_or_404(CourseOffering, pk=self.kwargs['pk'])
        context['course_offering'] = course_offering

        # Create a dictionary of initial values for each student
        initial_values = {}
        for student in course_offering.student.all():
            initial_values[student.pk] = {
                'student': student,
                'course_offering': course_offering,
                # 'is_present': True,  # Set the default value you want for is_present
                # 'attendance_date': '2023-11-08',  # Set the default date you want
                # 'remark': 'Your default remark',  # Set the default remark
            }

        print(initial_values)

        # Create a formset for all student forms with initial values
        AttendanceFormSet = modelformset_factory(Attendance, form=AttendanceForm, extra=0)
        student_forms = AttendanceFormSet(queryset=course_offering.student.all(), initial=initial_values)
       
        context['student_forms'] = student_forms
        # print(student_forms)
        # print(student_forms)
        return context

  