from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from report.models import Attendance
from report.form import AttendanceForm
from django.shortcuts import get_object_or_404
from program.models import CourseOffering
from django.urls import reverse
from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from datetime import datetime
# from customUser.models import Student
# Create your views here.

class AttendanceListView(DetailView):
    model = CourseOffering
    template_name = 'report/attendance/attendance_list.html'
    context_object_name = 'course_offering'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get attendance data for the course offering
        # getting all attendance data for the course offering selected 
        attendance_list = self.object.attendance_set.all()

        context['attendance_list'] = attendance_list
        return context

class AttendanceCreateView(CreateView):
    model=Attendance
    template_name='report/attendance/attendance_form.html'
    form_class=AttendanceForm
    field=['student','program_offering','course_offering','is_present','attendance_date','attendance_date']
    # success_url= reverse('program_offering_list') 
    def get_success_url(self):

        return reverse('program_offering_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You need to add code to get the course offering here, assuming you have a method or logic for that
        course_offering = get_object_or_404(CourseOffering, pk=self.kwargs['pk'])
        context['course_offering'] = course_offering
         # Create a form instance for each student in the course_offering
        student_forms = []
        for student in course_offering.student.all():
            student_form = self.form_class(initial={'student': student, 'course_offering': course_offering})
            student_forms.append(student_form)
        
        context['student_forms'] = student_forms
        return context
   
def mark_attendance(request, pk):
    course_offering = get_object_or_404(CourseOffering, id=pk)
    students = course_offering.student.all()
    today_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        # Get the selected date from the form
        selected_date = request.POST.get('attendanceDate')

        # Convert the selected date to a datetime object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')

        # Use the selected date for attendance_date
        for student in students:
            is_present = request.POST.get(f'is_present_{student.id}')
            remark = request.POST.get(f'remark_{student.id}')
            attendance, created = Attendance.objects.get_or_create(
                student=student, course_offering=course_offering, attendance_date=selected_date)

            attendance.is_present = is_present == 'present'
            attendance.remark = remark
            attendance.save()

        # Redirect to a success page or do something else
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'report/attendance/mark_attendance.html', {
        'course_offering': course_offering,
        'students': students,
        'today_date': today_date,
    })