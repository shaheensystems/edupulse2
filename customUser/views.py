from django.shortcuts import render
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from customUser.models import Student,Staff
from django.http import HttpResponseRedirect
from datetime import timedelta, datetime
from django.utils import timezone

# Create your views here.
class UserLoginView(LoginView):
    redirect_authenticated_user=True
    success_url=reverse_lazy("dashboard")
    template_name="auth/login.html"

    def form_invalid(self, form):
        print ("Invalid Login Credentials ")
        messages.error(self.request, " Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
    

class UserLogOutView(LoginRequiredMixin,LogoutView):
    success_url=reverse_lazy('dashboard')
    template_name='auth/logout.html'


class AllStudentsView(LoginRequiredMixin,ListView):
    model=Student
    template_name='students/students.html'
    context_object_name='students'
    
    def get_queryset(self):
        user = self.request.user
        print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return Student.objects.all()

        # Check if the user is a teacher
        elif user.groups.filter(name='Teacher').exists():
            # print("condition matched for teacher")
            # return CourseOffering.objects.filter(course__program__program_offerings__program_leader__staff=user)  
            # Teacher has no access for program 
            # return ProgramOffering.objects.filter(program__course__course_offering__staff=user)
            return Student.objects.filter(course_offerings__teacher__staff=user)
        
            # pass
        elif user.groups.filter(name='Program_Leader').exists():
            # return ProgramOffering.objects.none()
            return Student.objects.filter(course_offering__course__program__program_offering__program_leader__staff=user)  
        
        elif user.groups.filter(name='Student').exists():
            return Student.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return Student.objects.none()

class AllStudentsAtRiskView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/all_students_at_risk.html'
    context_object_name = 'students'

    def get_queryset(self):
        from report.models import WeeklyReport
      
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)
        students=Student.objects.all()

        at_risk_students = set()
        for student in students:
            all_weekly_reports_last_week = WeeklyReport.objects.filter(
                    student=student,
                    sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                )
                       
            if all_weekly_reports_last_week:
                for weekly_report in  all_weekly_reports_last_week:
                    if weekly_report.at_risk is True:
                        at_risk_students.add(student)
                     

        return at_risk_students
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        print(Student.objects.all())
        context['at_risk_students']=Student.objects.all()
        
        

        return context