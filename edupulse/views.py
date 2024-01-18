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
from django.db.models import Q,F,Count
from datetime import datetime, timedelta


from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offerings_student_enrollment,get_chart_data_course_offerings_student_enrollment,get_chart_data_student_and_Staff_by_campus,get_chart_data_student_enrollment_by_region,get_chart_data_programs_student_enrollment,get_chart_data_offering_type_student_enrollment,get_chart_data_attendance_report

from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,get_online_offline_program,default_start_and_end_date,filter_data_based_on_date_range
# def home(request):
    
#     return render(request,'index.html')

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # programs=Program.objects.all()
        # courses=Course.objects.all()
        # program_offerings=ProgramOffering.objects.all()
        # students=Student.objects.all()
        # course_offerings=CourseOffering.objects.all()
        # attendances=Attendance.objects.all()


        # programs_for_current_user=None
        # inactive_programs_for_current_user=None
        # online_programs_for_current_user=None
        # offline_programs_for_current_user=None

        


        # Program Offering Enrollment data for current user
        # print("current user group :",self.request.user.groups.all())
        # user_groups=self.request.user.groups.all()

        user_data=filter_database_based_on_current_user(request_user=self.request.user,
                                                        program_offerings=ProgramOffering.objects.all(),
                                                        course_offerings=CourseOffering.objects.all(),
                                                        programs=Program.objects.all(),
                                                        courses=Course.objects.all(),
                                                        students=Student.objects.all(),
                                                        attendances=Attendance.objects.all()
                                                        )
        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        # context.update(user_data)


        # if user_groups.filter(name="Head_of_School").exists() or user_groups.filter(name="Admin").exists():
        #     program_offerings_for_current_user=program_offerings
        #     course_offerings_for_current_user=course_offerings
        #     programs_for_current_user=programs
        #     courses_for_current_user=courses
        #     students=students
        #     all_programs=programs
            

        #     # for program in programs_for_current_user:
        #     #     print(program.temp_id,":",program.calculate_attendance_percentage())
            
        #     # Use Q objects to filter attendances for all students in the students queryset
        #     attendances = attendances.filter(student__in=students)
        # elif user_groups.filter(name="Program_Leader").exists():
        #     program_offerings_for_current_user=program_offerings.filter(program_leader=self.request.user.staff_profile)
        #     course_offerings_for_current_user=course_offerings.filter(course__program__program_offerings__program_leader=self.request.user.staff_profile)
        #     students=students.filter(program_offering__program_leader__staff=self.request.user)
            
        #     programs_for_current_user=None
        #     courses_for_current_user=None
        #     attendances = attendances.filter(student__in=students)
        #     all_programs=programs_for_current_user
        #     # print(attendances)
        #     # print(students)
        # elif user_groups.filter(name="Teacher").exists():
        #     program_offerings_for_current_user=program_offerings.filter(program__course__course_offering__teacher__staff=self.request.user)
        #     course_offerings_for_current_user=course_offerings.filter(teacher__staff=self.request.user)
        #     students=students.filter(course_offerings__teacher__staff=self.request.user)
        #     programs_for_current_user=None
        #     courses_for_current_user=None
        #     attendances = attendances.filter(student__in=students)
        #     all_programs=programs_for_current_user
        # #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
        # else:
        #     program_offerings_for_current_user=None
        #     course_offerings_for_current_user=None
        #     programs_for_current_user=None
        #     courses_for_current_user=None
        #     students=None
        #     attendances = None
        #     all_programs=programs_for_current_user

        
        
        # filter data with start and end date
        date_filter_form = DateFilterForm(self.request.GET)
        # print("context data ",user_data['program_offerings_for_current_user'])
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date

        if date_filter_form.is_valid():
            start_date=date_filter_form.cleaned_data['start_date']
            end_date=date_filter_form.cleaned_data['end_date']

            # if not start_date:
            #         # default_start_date = datetime.now() - timedelta(days=365)  # One year ago
            #         # default_start_date = datetime(datetime.now().year - 1, 1, 1).strftime('%Y-%m-%d')  # 1st Jan of lst year 
            #         start_date = default_start_date
            # if not end_date:
            #     # default_end_date=datetime.now().strftime('%Y-%m-%d')
            #     end_date=default_end_date


            
            # # filter data according to start and end date 
            # if start_date and end_date:

            #     if program_offerings_for_current_user is not None :
            #         program_offerings_for_current_user=program_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
            #     if course_offerings_for_current_user is not None :
            #         course_offerings_for_current_user=course_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
                
            #     # all program and course need to be shown 
            #     if programs_for_current_user is not None:

            #         active_programs = programs_for_current_user.filter(
            #                                                         Q(program_offerings__start_date__gte=start_date) &
            #                                                         Q(program_offerings__end_date__lte=end_date)
            #                                                   ).distinct()
            #         # Get the inactive programs (programs that do not match the date criteria)
            #         inactive_programs = programs_for_current_user.exclude(id__in=active_programs.values_list('id', flat=True))
                    
            #         programs_for_current_user = active_programs
            #         active_programs_for_current_user = active_programs

            #         inactive_programs_for_current_user=inactive_programs
            #         # print(len(programs_for_current_user))
            #         # print(len(inactive_programs_for_current_user))
                    

            #     if courses_for_current_user is not None:
            #         courses_for_current_user = courses_for_current_user.filter(
            #                                                         Q(course_offering__start_date__gte=start_date) &
            #                                                         Q(course_offering__end_date__lte=end_date)
            #                                                     ).distinct()
                
                
            #     if attendances is not None:
            #         attendances=attendances.filter(
            #             Q(attendance_date__gte=start_date)&
            #             Q(attendance_date__lte=end_date)
            #         ).distinct()

            #     # print(start_date,":",end_date)
            #     context['start_date']=start_date
            #     context['end_date']=end_date

            filtered_data_by_date_range=filter_data_based_on_date_range(
                                        start_date=start_date,
                                        end_date=end_date,
                                        programs_for_current_user=programs_for_current_user,
                                        courses_for_current_user=courses_for_current_user,
                                        program_offerings_for_current_user=program_offerings_for_current_user,
                                        course_offerings_for_current_user=course_offerings_for_current_user,
                                        attendances =attendances)
            
            program_offerings_for_current_user=filtered_data_by_date_range['program_offerings_for_current_user']
            course_offerings_for_current_user=filtered_data_by_date_range['course_offerings_for_current_user']
            programs_for_current_user=filtered_data_by_date_range['programs_for_current_user']
            courses_for_current_user=filtered_data_by_date_range['courses_for_current_user']
            active_programs_for_current_user=filtered_data_by_date_range['active_programs_for_current_user']
            inactive_programs_for_current_user=filtered_data_by_date_range['inactive_programs_for_current_user']
            attendances=filtered_data_by_date_range['attendances']
            context.update(filtered_data_by_date_range)
               
        context['date_filter_form']=date_filter_form




        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)

        # if programs_for_current_user is not None:
        #                 online_programs_for_current_user=programs_for_current_user.filter(
        #                                 Q(program_offerings__offering_mode="online")
        #                             )
        #                 offline_programs_for_current_user=programs_for_current_user.filter(
        #                             ~Q(program_offerings__offering_mode="online")
        #                         )
        # print("compare st by course offerings:")
        # print(get_total_no_of_student_by_course_offerings(course_offerings=course_offerings),": here unique")
        # print(len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings)))
       
        # print("compare st by program offerings:")
        # print(get_total_no_of_student_by_program_offerings(program_offerings=program_offerings),":here unique")
        # print(len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings)))
       

        # print("total students :",total_students_in_program_offerings_for_current_user)

        # # print("chart data programs and student:",get_chart_data_programs_student_enrollment(programs=programs_for_current_user))
        # print("chart data offering type student enrollment :",get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user))
        print(start_date,":",end_date)
        chart_data_student_enrollment_by_campus,chart_data_staff_enrollment_by_campus=get_chart_data_student_and_Staff_by_campus()
        # context['start_date']=start_date
        # context['end_date']=end_date
        context['chart_data_campus_enrollment_student'] = chart_data_student_enrollment_by_campus
        context['chart_data_campus_enrollment_staff'] = chart_data_staff_enrollment_by_campus
        context['chart_data_offering_mode_enrollment_students']=get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user)
        context['chart_data_programs_student_enrollment'] = get_chart_data_programs_student_enrollment(programs=all_programs)
        # context['chart_data_programs_student_enrollment'] = get_chart_data_programs_student_enrollment(programs=context['all_programs'])
        context['chart_data_program_offering_student_enrollment'] = get_chart_data_program_offerings_student_enrollment(program_offerings=program_offerings_for_current_user)
        context['chart_data_course_offering_student_enrollment'] = get_chart_data_course_offerings_student_enrollment(course_offerings=course_offerings_for_current_user)
        context['chart_data_student_region']=get_chart_data_student_enrollment_by_region(students=students)
        # context['chart_data_student_region']=get_chart_data_student_enrollment_by_region(students=context['students'])
        
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        context['attendances']=attendances

        # context['program_offerings']=program_offerings

        context['active_programs_for_current_user']=active_programs_for_current_user
        context['programs_for_current_user']=programs_for_current_user
        context['inactive_programs_for_current_user']=inactive_programs_for_current_user
        # context['online_programs_for_current_user']=online_programs_for_current_user
        # context['offline_programs_for_current_user']=offline_programs_for_current_user




        context['courses_for_current_user']=courses_for_current_user
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['course_offerings_for_current_user']=course_offerings_for_current_user
        context['total_students_in_program_offerings_for_current_user']=len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings_for_current_user))
        context['total_students_in_course_offerings_for_current_user']=len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings_for_current_user))

        # context['total_students_in_program_offerings_for_current_user']=total_unique_students_in_program_offerings_for_current_user
        # context['course_offerings']=course_offerings
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