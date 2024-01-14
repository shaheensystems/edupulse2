from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from report.models import Attendance
from base.models import Campus
from django.views.generic import DetailView,ListView,TemplateView
from program.models import ProgramOffering,CourseOffering,Program,Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from datetime import datetime
from .forms import DateFilterForm
from django.db.models import Q
from datetime import datetime, timedelta


from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offerings_student_enrollment,get_chart_data_course_offerings_student_enrollment,get_chart_data_student_and_Staff_by_campus,get_chart_data_student_enrollment_by_region,get_chart_data_programs_student_enrollment,get_chart_data_offering_type_student_enrollment,get_chart_data_attendance_report

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
        attendances=Attendance.objects.all()
        


        # Program Offering Enrollment data for current user
        # print("current user group :",self.request.user.groups.all())
        user_groups=self.request.user.groups.all()
        
        if user_groups.filter(name="Head_of_School").exists() or user_groups.filter(name="Admin").exists():
            program_offerings_for_current_user=program_offerings
            course_offerings_for_current_user=course_offerings
            programs_for_current_user=programs
            courses_for_current_user=courses
            students=students
            # Use Q objects to filter attendances for all students in the students queryset
            attendances = attendances.filter(student__in=students)
        elif user_groups.filter(name="Program_Leader").exists():
            program_offerings_for_current_user=program_offerings.filter(program_leader=self.request.user.staff_profile)
            course_offerings_for_current_user=course_offerings.filter(course__program__program_offerings__program_leader=self.request.user.staff_profile)
            students=students.filter(program_offering__program_leader__staff=self.request.user)
            
            programs_for_current_user=None
            courses_for_current_user=None
            attendances = attendances.filter(student__in=students)
            print(attendances)
            print(students)
        elif user_groups.filter(name="Teacher").exists():
            program_offerings_for_current_user=program_offerings.filter(program__course__course_offering__teacher__staff=self.request.user)
            course_offerings_for_current_user=course_offerings.filter(teacher__staff=self.request.user)
            students=students.filter(course_offerings__teacher__staff=self.request.user)
            programs_for_current_user=None
            courses_for_current_user=None
            attendances = attendances.filter(student__in=students)
           
        #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
        else:
            program_offerings_for_current_user=None
            course_offerings_for_current_user=None
            programs_for_current_user=None
            courses_for_current_user=None
            students=None
            attendances = None

        # filter data with start and end date
        date_filter_form = DateFilterForm(self.request.GET)
        if date_filter_form.is_valid():
            start_date=date_filter_form.cleaned_data['start_date']
            end_date=date_filter_form.cleaned_data['end_date']
            if not start_date:
                    # default_start_date = datetime.now() - timedelta(days=365)  # One year ago
                    default_start_date = datetime(datetime.now().year - 1, 1, 1)  # 1st Jan of lst year 
                    start_date = default_start_date.strftime('%Y-%m-%d')
            if not end_date:
                default_end_date=datetime.now().strftime('%Y-%m-%d')
                end_date=default_end_date


            
            # filter data according to start and end date 
            if start_date and end_date:
                if program_offerings_for_current_user is not None :
                    program_offerings_for_current_user=program_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
                if course_offerings_for_current_user is not None :
                    course_offerings_for_current_user=course_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
                if programs_for_current_user is not None:
                    programs_for_current_user = programs_for_current_user.filter(
                                                                    Q(program_offerings__start_date__gte=start_date) &
                                                                    Q(program_offerings__end_date__lte=end_date)
                                                              ).distinct()
                if courses_for_current_user is not None:
                    courses_for_current_user = courses_for_current_user.filter(
                                                                    Q(course_offering__start_date__gte=start_date) &
                                                                    Q(course_offering__end_date__lte=end_date)
                                                                ).distinct()
                
                
                if attendances is not None:
                    attendances=attendances.filter(
                        Q(attendance_date__gte=start_date)&
                        Q(attendance_date__lte=end_date)
                    ).distinct()

                print(start_date,":",end_date)
                context['start_date']=start_date
                context['end_date']=end_date
        context['date_filter_form']=date_filter_form

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
        
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        context['attendances']=attendances

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
        context['attendances']=attendances


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