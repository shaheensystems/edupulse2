from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from base.models import Campus
from django.views.generic import DetailView,ListView,TemplateView
from program.models import ProgramOffering,CourseOffering,Program,Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum



from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offerings_student_enrollment,get_chart_data_course_offerings_student_enrollment,get_chart_data_student_and_Staff_by_campus,get_chart_data_student_enrollment_by_region,get_chart_data_programs_student_enrollment,get_chart_data_offering_type_student_enrollment

# def home(request):
    
#     return render(request,'index.html')

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        programs=Program.objects.all()
        courses=Course.objects.all()
        program_offerings=ProgramOffering.objects.all()
        students=Student.objects.all()
        course_offerings=CourseOffering.objects.all()


        # Program Offering Enrollment data for current user
        # print("current user group :",self.request.user.groups.all())
        user_groups=self.request.user.groups.all()
        
        if user_groups.filter(name="Head_of_School").exists() or user_groups.filter(name="Admin").exists():
            program_offerings_for_current_user=program_offerings
            course_offerings_for_current_user=course_offerings
            programs_for_current_user=programs
            courses_for_current_user=courses
            students=students
        elif user_groups.filter(name="Program_Leader").exists():
            program_offerings_for_current_user=program_offerings.filter(program_leader=self.request.user.staff_profile)
            course_offerings_for_current_user=course_offerings.filter(course__program__program_offerings__program_leader=self.request.user.staff_profile)
            students=students.filter(program_offering__program_leader__staff=self.request.user)
            programs_for_current_user=None
            courses_for_current_user=None
            
        elif user_groups.filter(name="Teacher").exists():
            program_offerings_for_current_user=program_offerings.filter(program__course__course_offering__teacher__staff=self.request.user)
            course_offerings_for_current_user=course_offerings.filter(teacher__staff=self.request.user)
            students=students.filter(course_offerings__teacher__staff=self.request.user)
            programs_for_current_user=None
            courses_for_current_user=None
           
        #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
        else:
            program_offerings_for_current_user=None
            course_offerings_for_current_user=None
            programs_for_current_user=None
            courses_for_current_user=None
            students=None

   
       
        # print("compare st by course offerings:")
        # print(get_total_no_of_student_by_course_offerings(course_offerings=course_offerings),": here unique")
        # print(len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings)))
       
        # print("compare st by program offerings:")
        # print(get_total_no_of_student_by_program_offerings(program_offerings=program_offerings),":here unique")
        # print(len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings)))
       

        # print("total students :",total_students_in_program_offerings_for_current_user)

        # # print("chart data programs and student:",get_chart_data_programs_student_enrollment(programs=programs_for_current_user))
        # print("chart data offering type student enrollment :",get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user))

        chart_data_student_enrollment_by_campus,chart_data_staff_enrollment_by_campus=get_chart_data_student_and_Staff_by_campus()

        context['chart_data_campus_enrollment_student'] = chart_data_student_enrollment_by_campus
        context['chart_data_campus_enrollment_staff'] = chart_data_staff_enrollment_by_campus
        context['chart_data_offering_mode_enrollment_students']=get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user)
        context['chart_data_programs_student_enrollment'] = get_chart_data_programs_student_enrollment(programs=programs_for_current_user)
        context['chart_data_program_offering_student_enrollment'] = get_chart_data_program_offerings_student_enrollment(program_offerings=program_offerings_for_current_user)
        context['chart_data_course_offering_student_enrollment'] = get_chart_data_course_offerings_student_enrollment(course_offerings=course_offerings_for_current_user)
        context['chart_data_student_region']=get_chart_data_student_enrollment_by_region(students=students)


        context['program_offerings']=program_offerings

        context['programs_for_current_user']=programs_for_current_user
        context['courses_for_current_user']=courses_for_current_user
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['course_offerings_for_current_user']=course_offerings_for_current_user
        context['total_students_in_program_offerings_for_current_user']=len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings_for_current_user))
        context['total_students_in_course_offerings_for_current_user']=len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings_for_current_user))

        # context['total_students_in_program_offerings_for_current_user']=total_unique_students_in_program_offerings_for_current_user
        context['course_offerings']=course_offerings
        context['students']=students


        context['total_students_at_risk_query_set']=get_no_of_at_risk_students_by_program_offerings(program_offerings_for_current_user)


        # context['staff_profile'] = self.request.user.staff_profile
        # Check if the user has a staff_profile
        if hasattr(self.request.user, 'staff_profile'):
            context['staff_profile'] = self.request.user.staff_profile
        else:
            context['staff_profile'] = None

        # print("current user:", self.request.user.staff_profile)
        # print("staff profile:", self.request.user.staff_profile)
    
        # Add other necessary context data

        return context