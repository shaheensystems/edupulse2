from django.shortcuts import render
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,UpdateView,CreateView,TemplateView
from customUser.models import Student,Staff
from django.http import HttpResponseRedirect
from datetime import timedelta, datetime
from django.utils import timezone
from utils.function.helperGetAtRiskStudent import get_all_at_risk_student_last_week
from django.db.models import Q,Count
from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,filter_data_based_on_date_range,default_start_and_end_date


# Create your views here.
class UserLoginView(LoginView):
    redirect_authenticated_user=True
    success_url=reverse_lazy("dashboard")
    template_name="auth/login.html"

    def form_invalid(self, form):
        print ("Invalid Login Credentials ")
        messages.error(self.request, " Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
    

class UserLogOutView(LogoutView):
   
    success_url=reverse_lazy('dashboard')
    template_name='auth/logout.html'


class AllStudentsView(LoginRequiredMixin,ListView):
    model=Student
    template_name='students/students.html'
    context_object_name='students'


   
    def get_queryset(self):
        user = self.request.user
    
        
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date
        user_data=filter_database_based_on_current_user(request_user=self.request.user)
        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
        filtered_data_by_date_range=filter_data_based_on_date_range(
                                        start_date=start_date,
                                        end_date=end_date,
                                        programs_for_current_user=programs_for_current_user,
                                        courses_for_current_user=courses_for_current_user,
                                        program_offerings_for_current_user=program_offerings_for_current_user,
                                        course_offerings_for_current_user=course_offerings_for_current_user,
                                        attendances =attendances,
                                        weekly_reports=weekly_reports)
            
        program_offerings_for_current_user=filtered_data_by_date_range['program_offerings_for_current_user']
        course_offerings_for_current_user=filtered_data_by_date_range['course_offerings_for_current_user']
        programs_for_current_user=filtered_data_by_date_range['programs_for_current_user']
        courses_for_current_user=filtered_data_by_date_range['courses_for_current_user']
        active_programs_for_current_user=filtered_data_by_date_range['active_programs_for_current_user']
        inactive_programs_for_current_user=filtered_data_by_date_range['inactive_programs_for_current_user']
        attendances=filtered_data_by_date_range['attendances']
        weekly_reports=filtered_data_by_date_range['weekly_reports']
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

        # for student in students:
        #     if student.student_is_at_risk_for_last_week_status():
        #         print("Student at risk ")


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
        # count_no_prog_offering=0
        # count_no_course_offering=0
        # count_no_students_have_more_then_one_course_offering=0
        # for student in students:
        #     if not student.program_offering.exists():
        #         # print("student doesn't have program offering ",student)
        #         count_no_prog_offering+=1
        #     if student.program_offering.all() and len(student.program_offering.all())>1:
        #         count_no_students_have_more_then_one_course_offering+=1
        #     if not student.course_offerings.exists():
        #         # print("student doesn't have Course offering ",student)
        #         count_no_course_offering+=1
        
        student_not_enrolled_in_program_offering=students.filter(program_offering__isnull=True)
        student_not_enrolled_in_course_offering=students.filter(course_offerings__isnull=True)
        # Annotate the count of program offerings for each student
        students_with_program_count = students.annotate(program_count=Count('program_offering'))

        # Filter students with more than one program offering
        students_with_multiple_programs = students_with_program_count.filter(program_count__gt=1)
     
        context['student_not_enrolled_in_any_program_offering']=student_not_enrolled_in_program_offering
        context['student_not_enrolled_in_any_course_offering']=student_not_enrolled_in_course_offering
        context['student_enrolled_more_then_one_program_offering']=students_with_multiple_programs


        context['total_students']=students

        total_at_risk_students=students.filter(weekly_reports__at_risk=True)
        
        # context['total_at_risk_students']=self.get_at_risk_students(students)
        context['total_at_risk_students']=total_at_risk_students

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