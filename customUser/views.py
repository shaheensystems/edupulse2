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
from django.db.models import Q


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
            students=Student.objects.all()
            # print("S1:",students.count())
        elif user.groups.filter(name='Teacher').exists():
            students= Student.objects.filter(course_offerings__teacher__staff=user)
        elif user.groups.filter(name='Program_Leader').exists():
            students= Student.objects.filter(program_offering__program_leader__staff=user)  
        elif user.groups.filter(name='Student').exists():
            students= Student.objects.none()
        else:
            students=Student.objects.none()
        
        # for student in students:
            # print(student.student.campus)
            # print(student.course_offerings.all())
            # print(student.student.first_name)
        sort_by = self.request.GET.get('sort_by', 'student__first_name')  # Default to sorting by id
        search_query = self.request.GET.get('search', '')


        # Apply sorting
        
         # Apply sorting based on the selected option
        if sort_by == 'student_is_at_risk_for_last_week_status':
            students = sorted(students, key=lambda x: x.student_is_at_risk_for_last_week_status() or 0,reverse=True)
        elif sort_by=='calculate_attendance_percentage':
            students = sorted(students, key=lambda x: x.calculate_attendance_percentage() or 0 ,reverse=True)
        elif sort_by=='international_student':
             students = students.order_by(f"-{sort_by}")
        elif sort_by=='course_offerings': # filter is not working in any oder check later 
            students = students.order_by(f"-{sort_by}")
        elif sort_by=='program_offering': # filter is not working in any oder check later 
            students = students.order_by(f"-{sort_by}")
        elif sort_by=='student__campus':
            students = students.order_by(f"{sort_by}")
        elif sort_by=='student__first_name':
            students = students.order_by(f"{sort_by}")
        elif sort_by=='id':
            students = students.order_by(f"{sort_by}")
        else:
            students = students.order_by(f"-{sort_by}")

        for student in students:
            if student.student_is_at_risk_for_last_week_status():
                print("Student at risk ")


        # print("S2-1:",students.count())
        # print("S2-1:",Student.objects.all().count())
        # Apply filtering
        if search_query:
            students = students.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__campus__name__icontains=search_query) |
                Q(program_offering__program__name__icontains=search_query) |
                Q(course_offerings__course__name__icontains=search_query)
            ).distinct()


        # print("S2-2:",students.count())
        return students
    


    def get_at_risk_students(self,students):
     
        return get_all_at_risk_student_last_week(students=students)
       
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        students = context['students']
        # print("S3:",students.count())
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


        context['total_students']=students

       
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