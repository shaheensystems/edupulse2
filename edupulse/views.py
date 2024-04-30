from typing import Any
import json
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from report.models import Attendance
from base.models import Campus
from django.views import View
from django.views.generic import DetailView,ListView,TemplateView
from django.views.generic.edit import FormView
from program.models import ProgramOffering,CourseOffering,Program,Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from datetime import datetime
from .forms import DateFilterForm, ManageAttendanceFilterForm
from django.db.models import Q,F,Count,Case, When, Value, IntegerField,DurationField,ExpressionWrapper
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpRequest, JsonResponse
from django.db.models import Prefetch
from report.models import WeeklyReport
from django.utils.translation import gettext_lazy as _
from django.core.serializers import serialize
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from utils.function.BaseValues_List import ATTENDANCE_CHOICE, ATTENDANCE_COLOR_CHOICE, LOCALITY_COLOR_CHOICE, FINAL_STATUS_COLOR_CHOICE, ENGAGEMENT_COLOR_CHOICE
from django.utils import timezone

from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offerings_student_enrollment,get_chart_data_course_offerings_student_enrollment,get_chart_data_student_and_Staff_by_campus,get_chart_data_student_enrollment_by_region,get_chart_data_programs_student_enrollment,get_chart_data_offering_type_student_enrollment,get_chart_data_attendance_report

from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,get_online_offline_program,default_start_and_end_date,filter_data_based_on_date_range
from utils.function.helperAttendance import get_students_attendance_report_by_students
from utils.function.helperGetTableData import get_table_data_student_and_enrollment_count_by_programs,get_table_data_student_and_enrollment_count_by_campus_through_program_offerings, \
    get_barChart_data_student_attendance_details_by_programs,get_barChart_data_student_at_risk_status_by_programs,\
    get_barChart_data_student_by_locality_by_programs,get_barChart_data_student_engagement_status_by_programs,\
    get_barChart_data_student_attendance_details_by_campuses,get_barChart_data_student_at_risk_status_by_campuses,get_barChart_data_student_by_locality_by_campuses,get_barChart_data_student_engagement_status_by_courses,\
    get_table_data_student_and_enrollment_count_by_lecturer,get_barChart_data_student_attendance_details_by_lecturer,get_barChart_data_student_at_risk_status_by_lecturer,get_barChart_data_student_by_locality_by_lecturer,get_barChart_data_student_engagement_status_by_lecturer
# def home(request):
    
#     return render(request,'index.html')
class DashboardTestView(LoginRequiredMixin,TemplateView):
    template_name='dashboard-testing.html'
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)

        user_data=filter_database_based_on_current_user(request_user=self.request.user)

        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
        campuses=user_data['campuses']
        lecturer_qs_for_current_user=user_data['lecturer_qs_for_current_user']
        context.update(user_data)
        print("lecturer qs :",lecturer_qs_for_current_user," and lecturer count :",lecturer_qs_for_current_user.count())
     
        pl_program_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_programs(programs=programs_for_current_user)
        pl_campus_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(program_offerings=program_offerings_for_current_user)
        pl_lecturer_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_lecturer(lecturer_qs=lecturer_qs_for_current_user)
        print("pl_lecturer_wise_student_count_table_data:",pl_lecturer_wise_student_count_table_data)
        pl_student_count_table_data=[
            {'title':"Campus",'data_list':pl_campus_wise_student_count_table_data},
            {'title':"Program",'data_list':pl_program_wise_student_count_table_data},
            {'title':"Lecturer",'data_list':pl_lecturer_wise_student_count_table_data},    
        ]
        context['pl_student_count_button_list']=['Campus','Program','Lecturer']
        context['pl_campus_wise_student_count_table_data']=pl_campus_wise_student_count_table_data
        context['pl_student_count_table_data']=pl_student_count_table_data
        pl_program_wise_attendance_detail_data =get_barChart_data_student_attendance_details_by_programs(programs_for_current_user)
        pl_campus_wise_attendance_detail_data=get_barChart_data_student_attendance_details_by_campuses(campuses=campuses,program_offerings=program_offerings_for_current_user)
        context['pl_program_wise_attendance_detail_data']=pl_program_wise_attendance_detail_data
        context['pl_campus_wise_attendance_detail_data']=pl_campus_wise_attendance_detail_data
        context['attendance_choice']=dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))
        return context
    
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print( "get request initiated ......")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print( "get request send to ajax request handler ......")
            return self.handle_ajax_request(request,*args,**kwargs)
        
        return super().get(request, *args, **kwargs)
    
    
    def handle_ajax_request(self, request, *args, **kwargs):
        # Your logic for handling AJAX request
        pl_data_table_button_id = request.GET.get('pl_data_table_button_id')
        
        pl_id_student_count_table_title=request.GET.get('pl_id_student_count_table_title')
        
        pl_student_count_barChart_id=request.GET.get('pl_student_count_barChart_id')
        student_count_table_title=request.GET.get('student_count_table_title')

        context = self.get_context_data(**kwargs)

        if pl_data_table_button_id:
            print("pl student count  button data get .....:",pl_data_table_button_id)
            # program_offerings_for_current_user
            
            if pl_data_table_button_id=='id_data_table_button_campus':
                table_button_name="Campus"
                program_offerings_for_current_user = context.get('program_offerings_for_current_user')
                campuses = context.get('campuses')
                table_data=get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(program_offerings=program_offerings_for_current_user)
                programs_for_current_user = context.get('programs_for_current_user')
                bar_chart_attendance_data=get_barChart_data_student_attendance_details_by_campuses(campuses=campuses,program_offerings=program_offerings_for_current_user)
                chart_title='Campus wise Attendance - Enrollments'
            elif pl_data_table_button_id=='id_data_table_button_program':
                table_button_name="Program"
                programs_for_current_user = context.get('programs_for_current_user')
                table_data=get_table_data_student_and_enrollment_count_by_programs(programs=programs_for_current_user)
                bar_chart_attendance_data=get_barChart_data_student_attendance_details_by_programs(programs_for_current_user)
                chart_title='Program wise Attendance - Enrollments'
            elif pl_data_table_button_id=='id_data_table_button_lecturer':
                lecturer_qs_for_current_user = context.get('lecturer_qs_for_current_user')
                table_button_name="Lecturer"
                course_offerings_for_current_user=context.get('course_offerings_for_current_user')
                table_data=get_table_data_student_and_enrollment_count_by_lecturer(lecturer_qs=lecturer_qs_for_current_user)
                programs_for_current_user = context.get('programs_for_current_user')
                bar_chart_attendance_data=get_barChart_data_student_attendance_details_by_lecturer(lecturer_qs=lecturer_qs_for_current_user,course_offerings=course_offerings_for_current_user)
                chart_title='Lecturer wise Attendance - Enrollments'     
            else:
                table_button_name=""
                table_data=[]
                bar_chart_attendance_data=[]
                chart_title=''
                
            chart_subtitle_choice=dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))
            # Render HTML using a Django template
            html_content_student_count_table = render_to_string('components/dashboard/program_leader/components/pl_student_count_table_template.html', {
                    'table_button_name':table_button_name,
                    'table_data':table_data
                    
                    })
            html_content_student_count_barChart = render_to_string('components/dashboard/program_leader/components/pl_student_count_barChart.html', {
                    'title':chart_title,
                    'sub_title_choice':chart_subtitle_choice,
                    'data':bar_chart_attendance_data,
                    'student_count_table_title':table_button_name
                    
                    })

            return JsonResponse({
                'html_content_table': html_content_student_count_table, 
                'html_content_barChart': html_content_student_count_barChart, 
                'status':200})
    
        
        
        
        if pl_student_count_barChart_id:
            table_button_name=student_count_table_title
            print("initialising bar Chart data  for student count by button clicked id:",pl_student_count_barChart_id)    
        
            if pl_student_count_barChart_id=='id_pl_student_count_barChart_filter_btn_attendance':
                programs_for_current_user = context.get('programs_for_current_user')
                program_offerings_for_current_user = context.get('program_offerings_for_current_user')
                campuses = context.get('campuses')
                lecturer_qs_for_current_user = context.get('lecturer_qs_for_current_user')
                course_offerings_for_current_user = context.get('course_offerings_for_current_user')
                if table_button_name=='Campus':    
                    bar_chart_data=get_barChart_data_student_attendance_details_by_campuses(campuses=campuses,program_offerings=program_offerings_for_current_user)
                    chart_title='Campus wise Attendance - Enrollments'
                elif table_button_name=='Program':    
                    bar_chart_data=get_barChart_data_student_attendance_details_by_programs(programs_for_current_user)
                    chart_title='Program wise Attendance - Enrollments'
                elif table_button_name=='Lecturer':    
                    bar_chart_data=get_barChart_data_student_attendance_details_by_lecturer(lecturer_qs=lecturer_qs_for_current_user,course_offerings=course_offerings_for_current_user)
                    chart_title='Lecturer wise Attendance - Enrollments'
                else:
                    bar_chart_data=[]
                    chart_title='Student table Data not available '
                    
                chart_subtitle_choice=dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))
                
                
                
            elif pl_student_count_barChart_id=='id_pl_student_count_barChart_filter_btn_final_status':
                programs_for_current_user = context.get('programs_for_current_user')
                program_offerings_for_current_user = context.get('program_offerings_for_current_user')
                campuses = context.get('campuses')
                lecturer_qs_for_current_user=context.get('lecturer_qs_for_current_user')
                course_offerings_for_current_user=context.get('course_offerings_for_current_user')
                if table_button_name=='Campus':    
                    bar_chart_data=get_barChart_data_student_at_risk_status_by_campuses(campuses=campuses,program_offerings=program_offerings_for_current_user)
                    chart_title='Program wise Completion Status'
                    chart_title='Campus wise Completion Status'
                elif table_button_name=='Program':    
                    bar_chart_data=get_barChart_data_student_at_risk_status_by_programs(programs_for_current_user)
                    chart_title='Program wise Completion Status'
                elif table_button_name=='Lecturer':    
                    bar_chart_data=get_barChart_data_student_at_risk_status_by_lecturer(lecturer_qs=lecturer_qs_for_current_user,course_offerings=course_offerings_for_current_user)
                    chart_title='Lecturer wise Completion Status'
                else:
                    bar_chart_data=[]
                    chart_title='Student table Data not available '
                    
                chart_subtitle_choice=dict(sorted(FINAL_STATUS_COLOR_CHOICE.items()))
                
                
            elif pl_student_count_barChart_id=='id_pl_student_count_barChart_filter_btn_locality':
                programs_for_current_user = context.get('programs_for_current_user')
                campuses = context.get('campuses')
                lecturer_qs_for_current_user=context.get('lecturer_qs_for_current_user')
                course_offerings_for_current_user=context.get('course_offerings_for_current_user')
                program_offerings_for_current_user = context.get('program_offerings_for_current_user')
                if table_button_name=='Campus':    
                    bar_chart_data=get_barChart_data_student_by_locality_by_campuses(campuses=campuses,program_offerings=program_offerings_for_current_user)
                    chart_title='Campus wise Student Region'
                elif table_button_name=='Program':    
                    bar_chart_data=get_barChart_data_student_by_locality_by_programs(programs_for_current_user)
                    chart_title='Program wise Student Region'
                elif table_button_name=='Lecturer':    
                    bar_chart_data=get_barChart_data_student_by_locality_by_lecturer(lecturer_qs=lecturer_qs_for_current_user,course_offerings=course_offerings_for_current_user)
                    chart_title='Lecturer wise Student Region'
                else:
                    bar_chart_data=[]
                    chart_title='Student table Data not available '
                    
                chart_subtitle_choice=dict(sorted(LOCALITY_COLOR_CHOICE.items()))
                
                
                
                
            elif pl_student_count_barChart_id=='id_pl_student_count_barChart_filter_btn_engagement':
                programs_for_current_user = context.get('programs_for_current_user')
                campuses = context.get('campuses')
                program_offerings_for_current_user = context.get('program_offerings_for_current_user')
                lecturer_qs_for_current_user=context.get('lecturer_qs_for_current_user')
                course_offerings_for_current_user=context.get('course_offerings_for_current_user')
                if table_button_name=='Campus':    
                    bar_chart_data=get_barChart_data_student_engagement_status_by_courses(campuses=campuses,program_offerings=program_offerings_for_current_user)
                    chart_title='Campus wise Engagement Status'
                elif table_button_name=='Program':    
                    bar_chart_data=get_barChart_data_student_engagement_status_by_programs(programs_for_current_user)
                    chart_title='Program wise Engagement Status'
                elif table_button_name=='Lecturer':    
                    bar_chart_data=get_barChart_data_student_engagement_status_by_lecturer(lecturer_qs=lecturer_qs_for_current_user,course_offerings=course_offerings_for_current_user)
                    chart_title='Lecturer wise Engagement Status'
                else:
                    bar_chart_data=[]
                    chart_title='Student table Data not available '
                    
                chart_subtitle_choice=dict(sorted(ENGAGEMENT_COLOR_CHOICE.items()))
                
                
                
            else:
                bar_chart_data=[]
                chart_title=''
                chart_subtitle_choice=[]
            
            
            html_content_student_count_barChart = render_to_string('components/dashboard/program_leader/components/pl_student_count_barChart.html', {
                    'title':chart_title,
                    'sub_title_choice':chart_subtitle_choice,
                    'data':bar_chart_data,
                    'student_count_table_title':table_button_name
                    
                    })
            print("sending new barChart data to html page :")
            print(f" title :{chart_title}, sub title choice :{chart_subtitle_choice}, student count table title:{table_button_name} , data :{bar_chart_data}")
            if html_content_student_count_barChart:  
                # print("html page:",html_content_student_count_barChart)
                return JsonResponse({
                        'html_content_barChart': html_content_student_count_barChart, 
                        'status':200})
            else:
                return JsonResponse(
                    {
                    'error': 'Program ID not provided', 
                    'message':'no data available for view ',
                    },
                    status=400)
        
        
        return JsonResponse({'error': 'Program ID not provided'}, status=400)
        
class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_data=filter_database_based_on_current_user(request_user=self.request.user)

        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
        campuses=user_data['campuses']
        context.update(user_data)

        print("View program for current user before date filter :",programs_for_current_user)
        
        context['date_filter_form']=DateFilterForm()

        # print("View program for current user after date filter :",filtered_data_by_date_range['programs_for_current_user'])


        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)



        # # print("chart data programs and student:",get_chart_data_programs_student_enrollment(programs=programs_for_current_user))
        # print("chart data offering type student enrollment :",get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user))
        # print("data intialise with start and end date :",start_date,":",end_date)
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
        
        # when filter applies for Attendance Engagement and action page data will be change for attendance 
        # 1. attendance  filter by program 
        # 2. attendance filter by week , week start from program offering start date 
        # 3. attendance filter by session , each week has session 1 and session 2 according to the date 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        context['attendances']=attendances

        # context['program_offerings']=program_offerings

        # context['active_programs_for_current_user']=active_programs_for_current_user
        context['programs_for_current_user']=programs_for_current_user
        # context['inactive_programs_for_current_user']=inactive_programs_for_current_user
        # context['online_programs_for_current_user']=online_programs_for_current_user
        # context['offline_programs_for_current_user']=offline_programs_for_current_user




        context['courses_for_current_user']=courses_for_current_user
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['course_offerings_for_current_user']=course_offerings_for_current_user
        if get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings_for_current_user) is not None:
            context['total_students_in_program_offerings_for_current_user']=len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings_for_current_user))
        else:
            context['total_students_in_program_offerings_for_current_user']=0
        
        if get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings_for_current_user) is not None:
               
            context['total_students_in_course_offerings_for_current_user']=len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings_for_current_user))
        else:
            context['total_students_in_course_offerings_for_current_user']=0
            

        # context['total_students_in_program_offerings_for_current_user']=total_unique_students_in_program_offerings_for_current_user
        # context['course_offerings']=course_offerings
        
        print("Programs for current User :",programs_for_current_user)
        context['students']=students
        # Construct the query for blended and micro cred offerings
        blended_query = Q(student_enrollments__course_offering__offering_mode='micro cred') | \
                Q(student_enrollments__course_offering__offering_mode='blended')
        if students:
            blended_students=students.filter(blended_query)
            blended_students=students.exclude(Q(student_enrollments__course_offering__offering_mode = 'online') )
            online_students=students.filter(Q(student_enrollments__course_offering__offering_mode = 'online') )
        else:
            blended_students=None
            online_students=None
            
        if blended_students :
            context['total_students_in_blended_course_offerings']=set(blended_students)
        else:
            context['total_students_in_blended_course_offerings']=None
        
        if online_students:
            context['total_students_in_online_course_offerings']=set(online_students)
        else:
            context['total_students_in_online_course_offerings']=None

        
        enrolled_students=[]
        enrolled_students_for_blended_course_offerings=[]
        enrolled_students_for_online_course_offerings=[]
        if course_offerings_for_current_user:
            
            for co in course_offerings_for_current_user:
                for r in co.student_enrollments.all():
                    new_student=r.student
                    if co.offering_mode=='online':
                        enrolled_students_for_online_course_offerings.append(new_student)
                    else:
                        enrolled_students_for_blended_course_offerings.append(new_student)
                    enrolled_students.append(new_student)
                # print(enrolled_students)
        
        
        context['total_students_enrollment']=enrolled_students
        context['total_enrollment_in_blended_course_offerings']=enrolled_students_for_blended_course_offerings
        context['total_enrollment_in_online_course_offerings']=enrolled_students_for_online_course_offerings
        context['total_students_at_risk_query_set']=get_no_of_at_risk_students_by_program_offerings(program_offerings_for_current_user)
        context['attendances']=attendances
        context['student_attendance_percentage']=get_students_attendance_report_by_students(students=students)
        context['staff_profile'] = self.request.user.staff_profile if hasattr(self.request.user, 'staff_profile') else None

        
        pl_program_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_programs(programs=programs_for_current_user)
        pl_campus_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(program_offerings=program_offerings_for_current_user)
        pl_course_offerings_wise_student_count_table_data=get_table_data_student_and_enrollment_count_by_lecturer_through_course_offerings(course_offerings=course_offerings_for_current_user)
        
        pl_student_count_table_data=[
            {'title':"Campus",'data_list':pl_campus_wise_student_count_table_data},
            {'title':"Program",'data_list':pl_program_wise_student_count_table_data},
            {'title':"Lecturer",'data_list':pl_course_offerings_wise_student_count_table_data},    
        ]

        context['pl_student_count_table_data']=pl_student_count_table_data
        program_wise_sample_attendance_data=[
            {'program':'program 1' ,
             'attendance_percentage':{
                "present":10,
                'absent':30,
                'informed_absent':40,
                'tardy':20
            }
             },
            {'program':'program 2' ,
             'attendance_percentage':{
                "present":30,
                'absent':10,
                'informed_absent':10,
                'tardy':50
            }}
        ]
        campus_wise_sample_attendance_data=[
            {'campus':'campus 1' ,
             'attendance_percentage':{
                "present":20,
                'absent':10,
                'informed_absent':30,
                'tardy':40
            }
             },
            {'campus':'campus 2' ,
             'attendance_percentage':{
                "present":30,
                'absent':10,
                'informed_absent':20,
                'tardy':40
            }}
        ]
        lecturer_wise_sample_attendance_data=[
            {'lecturer':'lecturer 1' ,
             'attendance_percentage':{
                "present":18,
                'absent':12,
                'informed_absent':25,
                'tardy':45
            }
             },
            {'lecturer':'lecturer 2' ,
             'attendance_percentage':{
                "present":85,
                'absent':10,
                'informed_absent':3,
                'tardy':2
            }}
        ]
        
        
        
        
        
        pl_program_wise_attendance_detail_data =get_barChart_data_student_attendance_details_by_programs(programs_for_current_user)
        
        pl_student_count_table_campus_wise_barChart_data=[
            {
                'title':'Attendance',
                'sub_heading_list':ATTENDANCE_CHOICE,
                'data_list':pl_program_wise_attendance_detail_data
             },
            {
                'title':'Final Status',
                'sub_heading_list':ATTENDANCE_CHOICE,
                'data_list':pl_program_wise_attendance_detail_data
             },
            {
                'title':'Locality',
                'sub_heading_list':ATTENDANCE_CHOICE,
                'data_list':pl_program_wise_attendance_detail_data
             },
            {
                'title':'Engagement',
                'sub_heading_list':ATTENDANCE_CHOICE,
                'data_list':pl_program_wise_attendance_detail_data
             }
        ]
        
        context['pl_program_wise_attendance_detail_data']=pl_program_wise_attendance_detail_data
        context['attendance_choice']=ATTENDANCE_CHOICE

        # Add other necessary context data

        return context
    
    def get(self,request,*args,**kwargs):
        # Check if the request is coming from the date filter form
        if 'start_date' in request.GET or 'end_date' in request.GET:
            print("Initialise date filter logic from dashboard page")
            # Logic for handling GET request from the date filter form
            # Update the context data with filtered data based on the date range
            return self.handle_date_filter_request(request, *args, **kwargs)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("Initialise Attendance Engagement Action chart changes from dashboard page")
            # AJAX Request
            return self.handle_ajax_request(request, *args, **kwargs)
            
        # Non-AJAX Request
        print( " no ajax request found ")
        # Handle non-AJAX requests here, possibly by rendering a template
        return super().get(request, *args, **kwargs)
        
    def handle_date_filter_request(self, request, *args, **kwargs):
       
        # Your existing logic for handling date filter request
        context = self.get_context_data(**kwargs)
        # Add your date filter logic here
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date
        if 'start_date' in request.GET or 'end_date' in request.GET:
            # Logic for date filtering
            date_filter_form = DateFilterForm(request.GET)

            programs_for_current_user=context['programs_for_current_user']
            courses_for_current_user=context['courses_for_current_user']
            program_offerings_for_current_user=context['program_offerings_for_current_user']
            course_offerings_for_current_user=context['course_offerings_for_current_user']
            attendances=context['attendances']
            weekly_reports=context['weekly_reports']
            campuses=context['campuses']
            
            if date_filter_form.is_valid():
                start_date = date_filter_form.cleaned_data['start_date']
                end_date = date_filter_form.cleaned_data['end_date']
                # Apply date filtering logic here
                # filtered_data = filter_data_based_on_date_range(start_date, end_date)
                # print("sent program for current user for date filter :",programs_for_current_user)
                filtered_data_by_date_range=filter_data_based_on_date_range(
                                            start_date=start_date,
                                            end_date=end_date,
                                            programs_for_current_user=programs_for_current_user,
                                            courses_for_current_user=courses_for_current_user,
                                            program_offerings_for_current_user=program_offerings_for_current_user,
                                            course_offerings_for_current_user=course_offerings_for_current_user,
                                            attendances =attendances,
                                            weekly_reports=weekly_reports,
                                            campuses=campuses)
                
                program_offerings_for_current_user=filtered_data_by_date_range['program_offerings_for_current_user']
                course_offerings_for_current_user=filtered_data_by_date_range['course_offerings_for_current_user']
                programs_for_current_user=filtered_data_by_date_range['programs_for_current_user']
                courses_for_current_user=filtered_data_by_date_range['courses_for_current_user']
                active_programs_for_current_user=filtered_data_by_date_range['active_programs_for_current_user']
                inactive_programs_for_current_user=filtered_data_by_date_range['inactive_programs_for_current_user']
                attendances=filtered_data_by_date_range['attendances']
                weekly_reports=filtered_data_by_date_range['weekly_reports']
                campuses=filtered_data_by_date_range['campuses']
                context.update(filtered_data_by_date_range)  
                
        
                context['date_filter_form'] = date_filter_form
        return render(request, self.template_name, context)
        
    
    def handle_ajax_request(self, request, *args, **kwargs):
        # Your logic for handling AJAX request
        program_id = request.GET.get('program_id')
        week_no=request.GET.get('week_no')
        session_no=request.GET.get('session_no')
        print(f" data received from get request program Id : {program_id} , Week No ;{ week_no} and session No :{session_no}")
        print("program id ",program_id)
        print("week no ",week_no)
        print("session no ",session_no)
        context = self.get_context_data(**kwargs)
        attendances = context.get('attendances')
        print("Getting attendance from context...")
        if program_id or week_no or session_no:
           
            if program_id:
                attendances = attendances.filter(course_offering__student_enrollments__program_offering__program_id=program_id)
            else:
                attendances=attendances
            
           
            if week_no:
                print(f"Week filter initiated .... for week no :{week_no}")
                # attendances = attendances.annotate(
                #     calculated_week_no= ExpressionWrapper(
                #         (F('attendance_date') - F('course_offering__start_date')) // 7 + 1 ,
                #         output_field=IntegerField()
                #     ) 
                # )
                week_filter = F('course_offering__start_date__week') + week_no - 1
    
                # Filter attendances based on the calculated week number
                attendances = attendances.filter(attendance_date__week=week_filter)
                for a in attendances:
                    # print("week number",a.get_week_no() ,"and compare to week number value received from drop down :",week_no ," and that week lead to week number as per calender :",week_filter)
                    # print(f"{type(a.get_week_no())}: {type(week_no)}")
                    if a.week_no != int(week_no):
                        
                        print(" error in week number filter ")
            else:
                attendances=attendances
                
            if session_no:
                print("session filter initiated ....")
                attendances=attendances.order_by('attendance_date')
                attendances = attendances.annotate(
                                calculated_session_no=Case(
                                    When(course_offering__attendances__attendance_date__lte=F('attendance_date'), then=Value(2)),
                                    default=Value(1),
                                    output_field=IntegerField()
                                )
                
                         )
                # i=0  
                # for a in attendances:
                #     print(f" course offering :{a.course_offering} , attendance date {a.attendance_date} and week no :{a.get_week_no()}, session: {a.calculated_session_no}")
                #     session_from_model=a.get_session_no()
                #     print(f"session by model {session_from_model} : by annotate function{a.calculated_session_no}")
                #     if session_from_model != a.calculated_session_no:
                #         print("data not matched ")
                #     i+=1
                #     if i==100:
                #         break
                
                # Assuming you have implemented the get_session_no method in your Attendance model
                attendances = attendances.filter(calculated_session_no=session_no)
            else:
                attendances=attendances
            
            print("Filtered attendance data...",attendances)
            
            chart_data_attendance_report_attendance, chart_data_attendance_report_engagement, chart_data_attendance_report_action = get_chart_data_attendance_report(
                attendances=attendances)
            # Update context with chart data
            context.update({
            'chart_data_attendance_report_attendance': chart_data_attendance_report_attendance,
            'chart_data_attendance_report_engagement': chart_data_attendance_report_engagement,
            'chart_data_attendance_report_action': chart_data_attendance_report_action
            })

            
            # Render HTML using a Django template
            html_content = render_to_string('components/dashboard/student_attendance_engagement_action_report.html', {
                    'title':"Student Performance" ,
                    'chart1_data':chart_data_attendance_report_attendance ,
                    'chart2_data':chart_data_attendance_report_engagement,
                    'chart3_data':chart_data_attendance_report_action ,
                    'chart1_title':'Overall Attendance',
                    'chart2_title':'Absent Engagement Analysis' ,
                    'chart3_title':'Action Engagement Analysis' ,
                    'chart1_id':'attendance-chart',
                    'chart2_id':'engagement-chart',
                    'chart3_id':'action-chart',
                    'programs_for_current_user':context['programs_for_current_user']
                    })

            return JsonResponse({'html_content': html_content, 'status':200})
    
        else:
            return JsonResponse({'error': 'Program ID not provided'}, status=400)   
        
class ManageAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = 'report/manage_attendance.html'
    context_object_name = 'course_offerings'
    
    
    def get_queryset(self):
        # Assuming you want to filter course offerings based on the user
        
        user_data=filter_database_based_on_current_user(request_user=self.request.user)

        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
      
        course_offerings= course_offerings_for_current_user
        # course_offerings=CourseOffering.objects.prefetch_related(
        #     'teacher',
        #     'student',
        #     'teacher__staff',
        #     'attendances',
        #     Prefetch('weekly_reports', queryset=WeeklyReport.objects.prefetch_related('sessions'))
        # ).filter(staff_course_offering_relations__staff__staff=self.request.user)
        
        # print("manage Attendance CO :",course_offerings)
        return course_offerings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_offerings'] = self.get_queryset()
        # print(context['course_offerings'])
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # AJAX request
            course_offering_id = request.GET.get('course_offering_id')
            if course_offering_id:
                course_offering = get_object_or_404(CourseOffering, temp_id=course_offering_id)
                students = course_offering.student.all()
                # week_numbers = course_offering.get_week_numbers()
                week_numbers = [str(week_number[1]) for week_number in course_offering.get_week_numbers()]
                # print("course_offering",course_offering,"-","week Number:",week_numbers)
                serialized_students = [{'id': student.temp_id, 'first_name': student.student.first_name, 'last_name': student.student.last_name} for student in students]
                
                # print("W N",week_numbers)
                # print("S",serialized_students)
                response_data = {
                    'students': serialized_students,
                    'week_numbers': week_numbers,
                }
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({'error': 'Course offering ID is required'}, status=400)
        else:
            # Non-AJAX request
            context = self.get_context_data()
            # # Load values from localStorage
            # course_offering_filter = request.GET.get('course_offering_filter')
            # week_number_filter = request.GET.get('week_number_filter')
            # student_filter = request.GET.get('student_filter')
            # Add default values for form fields
            default_course_offering_id = context['course_offerings'].first().temp_id if context['course_offerings'] else None
            default_week_number = '1'  # Set your default week number here
            default_student_id = context['course_offerings'].first().student.first().temp_id if context['course_offerings'] and context['course_offerings'].first().student.first() else None
            # # Set default values from localStorage if available
            # if course_offering_filter:
            #     default_course_offering_id = course_offering_filter
            # if week_number_filter:
            #     default_week_number = week_number_filter
            # if student_filter:
            #     default_student_id = student_filter
                
            context['default_course_offering_id'] = default_course_offering_id
            context['default_week_number'] = default_week_number
            context['default_student_id'] = default_student_id
            return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            course_offering_id = request.POST.get('course_offering')
            week_number = request.POST.get('week_number')
            student_id = request.POST.get('student')
            # print("Post :",course_offering_id,student_id,week_number)
            if course_offering_id and week_number :
                course_offering = get_object_or_404(CourseOffering, temp_id=course_offering_id)
                
                start_date = course_offering.start_date + timedelta(weeks=int(week_number) - 1)
                end_date=start_date+timedelta(days=7)
                # Retrieve weekly report data based on course offering, week number, and student
                # Replace this with your actual logic to fetch weekly report data
                weekly_report_data = course_offering.weekly_reports.all()  # Implement your logic here
                
                weekly_report_data=weekly_report_data.filter(Q(sessions__attendance_date__gte=start_date) & Q(sessions__attendance_date__lte=end_date))

                # serialized_weekly_reports = serializers.serialize('json', weekly_report_data)
                
                # return JsonResponse(serialized_weekly_reports,safe=False, status=200)
                if student_id:

                    student = get_object_or_404(Student, temp_id=student_id)
                    weekly_report_data=weekly_report_data.filter(student=student)
                else:
                    student=None
                    
                # Render HTML using a Django template
                html_content = render_to_string('components/weekly_reports/weekly_reports_list.html', {
                    'weekly_reports': weekly_report_data,
                    'course_offering':course_offering,
                    'week_number':week_number,
                    'student':student,
                    })

                return JsonResponse({'html_content': html_content}, status=200)
            else:
                return JsonResponse({'error': 'Course offering ID, week number, and student ID are required'}, status=400)
        else:
            return JsonResponse({'error': 'This endpoint accepts only AJAX requests'}, status=400)   


class SaveWeeklyReportsView(View):
    def post(self, request):
        print("save weekly report request received ")
        # Process the POST request data here
        # For example, you can retrieve the data from the request and save it to the database
        # Make sure to handle any errors that might occur during saving
        
        # For demonstration purposes, let's assume we receive JSON data with weekly report details
        data = request.POST.get('data')  # Assuming the data is sent as JSON in the request
        # Process the data and save it to the WeeklyReport model
        # For example:
        try:
            # Parse the JSON data
            weekly_reports_data = json.loads(data)
            for report_data in weekly_reports_data:
                weekly_report = WeeklyReport.objects.get(pk=report_data['id'])
                weekly_report.engagement = report_data['engagement']
                weekly_report.action = report_data['action']
                # Set other fields accordingly
                weekly_report.save()
                
            return JsonResponse({'success': True, 'message': 'Weekly reports saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)