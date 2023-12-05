from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from report.models import Attendance,WeeklyReport
from report.form import AttendanceForm,WeeklyReportEditForm
from django.shortcuts import get_object_or_404
from program.models import CourseOffering
from django.urls import reverse
from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from django.views import View
from datetime import datetime
from django.db.models import Sum, Count,When,Case
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# from customUser.models import Student
# Create your views here.

def get_week_number(startingDate,currentDate):
    startingDate = datetime.combine(startingDate, datetime.min.time())
    currentDate = datetime.combine(currentDate, datetime.min.time())
    delta=currentDate-startingDate
    weeks=delta.days//7

    return weeks +1

class AttendanceListView(LoginRequiredMixin,DetailView):
    model = CourseOffering
    template_name = 'report/attendance/attendance_list.html'
    context_object_name = 'course_offering'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get attendance data for the course offering in ascending order 
        attendance_list = self.object.attendance.values('attendance_date').annotate(
            total_present=Count(Case(When(is_present='present', then=1))),
            total_students=Count('student')
        ).order_by('attendance_date')
        
        # Calculate the week number starting from the course start date
        course_start_date = self.object.start_date
    
        for attendance in attendance_list:
            # delta = attendance['attendance_date'] - course_start_date
            # attendance['week_number'] = (delta.days // 7) + 1
            attendance['week_number'] = get_week_number(course_start_date,attendance['attendance_date'])
            # print(attendance['week_number'])


        current_week_number =0
        current_session_number=0
        for attendance in attendance_list:
            new_week_number=attendance['week_number']
            if current_week_number==new_week_number:
               new_session_number=current_session_number+1
            else:
                new_session_number=1
            attendance['session_number']=new_session_number
            current_session_number=new_session_number
            current_week_number=new_week_number



        context['attendance_list'] = attendance_list
        return context
    
   

class AttendanceCreateView(LoginRequiredMixin,CreateView):
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
@login_required(login_url='user-login') 
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
            attendance.is_present = is_present 
            attendance.remark = remark
            attendance.save()
        
            # generate weekly report for each student while marking attendance  with the attendance 
            weekly_report, created = WeeklyReport.objects.get_or_create(
                student=student, course_offering=course_offering, week_number=get_week_number(course_offering.start_date,selected_date))

            weekly_report.sessions.add(attendance)
            weekly_report.save()
            
        # Redirect to a success page or do something else
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'report/attendance/mark_attendance.html', {
        'course_offering': course_offering,
        'students': students,
        'today_date': today_date,
    })


class WeeklyReportView(LoginRequiredMixin, DetailView):
    model = CourseOffering
    template_name = 'report/attendance/weekly_report_list.html'
    context_object_name = 'course_offering'
    
@login_required(login_url='user-login') 
def edit_weekly_report(request, pk,week_number):
    print(week_number)
    print("PK: ",pk)
    course_offering = get_object_or_404(CourseOffering, id=pk)
    # Retrieve a list of WeeklyReport objects for the given week_number and course_offering
    weekly_reports = WeeklyReport.objects.filter(week_number=week_number, course_offering=course_offering)
    students = course_offering.student.filter(weekly_reports__week_number=week_number).distinct()
    print(weekly_reports)
    for weekly_report in weekly_reports:
        print(f"Weekly Report: {weekly_report.week_number}")
        for session in weekly_report.sessions.all():
            print(f"  Session: {session.attendance_date}, Is Present: {session.is_present}")

    if request.method == 'POST':
        print("saving report initialise")

        # Use the selected date for attendance_date
        for weekly_report in weekly_reports:
            action = request.POST.get(f'action_{weekly_report.id}')
            engagement = request.POST.get(f'engagement_{weekly_report.id}')
            follow_up = request.POST.get(f'follow_up_{weekly_report.id}')
            assessment_status = request.POST.get(f'assessment_status_{weekly_report.id}')
            at_risk_value = request.POST.get(f'at_risk_{weekly_report.id}')
            # print("at risk value :",at_risk_value)
            # update weekly report data 
            weekly_report.action=action
            weekly_report.engagement=engagement
            weekly_report.follow_up=follow_up
            weekly_report.assessment_status=assessment_status
            if at_risk_value == "true":
                weekly_report.at_risk = True
            elif at_risk_value == "false":
                weekly_report.at_risk = False
            else:
                weekly_report.at_risk = None  # or handle the case when the value is not True or False
            
            weekly_report.save()
            print("weekly report saved : ",weekly_report)
            # print("weekly report at risk value saved : ",weekly_report.at_risk)
            # print("weekly report at assessment status  saved : ",weekly_report.assessment_status)
            
        # Redirect to a success page or do something else
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # return HttpResponseRedirect(reverse('edit_weekly_report', args=[pk, week_number]))
        return redirect('weekly_report_list', course_offering.pk)

    return render(request, 'report/attendance/edit_weekly_report.html', {
        'weekly_reports': weekly_reports,
        'students': students,
        'week_number':week_number,
        'course_offering':course_offering
       
    })

