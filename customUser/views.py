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
from utils.function.helperGetAtRiskStudent import get_all_at_risk_student_last_week
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
        # print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return Student.objects.all()

        elif user.groups.filter(name='Teacher').exists():
            return Student.objects.filter(course_offerings__teacher__staff=user)
        elif user.groups.filter(name='Program_Leader').exists():
            # return ProgramOffering.objects.none()
            # return Student.objects.filter(course_offerings__course__program__program_offerings__program_leader__staff=user)  
            return Student.objects.filter(program_offering__program_leader__staff=user)  

        elif user.groups.filter(name='Student').exists():
            return Student.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return Student.objects.none()
    

    def get_allowed_students(self):
        user = self.request.user
        # print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return Student.objects.all()

        elif user.groups.filter(name='Teacher').exists():
           
            return Student.objects.filter(course_offerings__teacher__staff=user)
        
        
            # pass
        elif user.groups.filter(name='Program_Leader').exists():
            # return ProgramOffering.objects.none()
            return Student.objects.filter(course_offerings__course__program__program_offerings__program_leader__staff=user)  
        
        elif user.groups.filter(name='Student').exists():
            return Student.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return Student.objects.none()

    def get_at_risk_students(self,students):
     
        return get_all_at_risk_student_last_week(students=students)
       
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = context['students']

        count_no_prog_offering=0
        count_no_course_offering=0
        count_no_students_have_more_then_one_course_offering=0
        for student in students:
            if not student.program_offering.exists():
                # print("student doesn't have program offering ",student)
                count_no_prog_offering+=1
            if student.program_offering.all() and len(student.program_offering.all())>1:
                count_no_students_have_more_then_one_course_offering+=1
            if not student.course_offerings.exists():
                # print("student doesn't have Course offering ",student)
                count_no_course_offering+=1
     
        context['student_not_enrolled_in_any_program_offering']=count_no_prog_offering
        context['student_not_enrolled_in_any_course_offering']=count_no_course_offering
        context['student_enrolled_more_then_one_program_offering']=count_no_students_have_more_then_one_course_offering


        context['total_students']=Student.objects.all()

       
        context['total_at_risk_students']=self.get_at_risk_students(students)

        return context

from utils.function.helperGetAtRiskStudent import get_all_at_risk_student_last_week

class AllStudentsAtRiskView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/all_students_at_risk.html'
    context_object_name = 'students'

    def get_queryset(self):
        
        students=Student.objects.all()

        at_risk_students = get_all_at_risk_student_last_week(students)
      
 
        return at_risk_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        print(Student.objects.all())
        context['at_risk_students']=Student.objects.all()

        return context