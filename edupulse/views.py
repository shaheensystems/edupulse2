from typing import Any
import json
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
from django.db.models import Q,F,Count
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Prefetch
from report.models import WeeklyReport
from django.utils.translation import gettext_lazy as _
from django.core.serializers import serialize
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from utils.function.BaseValues_List import ATTENDANCE_CHOICE

from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offerings_student_enrollment,get_chart_data_course_offerings_student_enrollment,get_chart_data_student_and_Staff_by_campus,get_chart_data_student_enrollment_by_region,get_chart_data_programs_student_enrollment,get_chart_data_offering_type_student_enrollment,get_chart_data_attendance_report

from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,get_online_offline_program,default_start_and_end_date,filter_data_based_on_date_range
from utils.function.helperAttendance import get_students_attendance_report_by_students
# def home(request):
    
#     return render(request,'index.html')

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
        # context.update(user_data)

        print("View program for current user before date filter :",programs_for_current_user)
        # filter data with start and end date
        date_filter_form = DateFilterForm(self.request.GET)
        # print("context data ",user_data['program_offerings_for_current_user'])
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date
        
        
        if date_filter_form.is_valid():
            start_date=date_filter_form.cleaned_data['start_date']
            end_date=date_filter_form.cleaned_data['end_date']
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
               
        context['date_filter_form']=date_filter_form

        # print("View program for current user after date filter :",filtered_data_by_date_range['programs_for_current_user'])


        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)



        # # print("chart data programs and student:",get_chart_data_programs_student_enrollment(programs=programs_for_current_user))
        # print("chart data offering type student enrollment :",get_chart_data_offering_type_student_enrollment(course_offerings=course_offerings_for_current_user))
        print("data intialise with start and end date :",start_date,":",end_date)
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
        blended_students=students.filter(blended_query)
        blended_students=students.exclude(Q(student_enrollments__course_offering__offering_mode = 'online') )
        online_students=students.filter(Q(student_enrollments__course_offering__offering_mode = 'online') )

        
        context['total_students_in_blended_course_offerings']=set(blended_students)
        context['total_students_in_online_course_offerings']=set(online_students)

        
        enrolled_students=[]
        enrolled_students_for_blended_course_offerings=[]
        enrolled_students_for_online_course_offerings=[]
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
        # Check if the user has a staff_profile
        # if hasattr(self.request.user, 'staff_profile'):
        #     context['staff_profile'] = self.request.user.staff_profile
        # else:
        #     context['staff_profile'] = None

        
        context['staff_profile'] = self.request.user.staff_profile if hasattr(self.request.user, 'staff_profile') else None

        
        # print("current user:", self.request.user.staff_profile)
        # print("staff profile:", self.request.user.staff_profile)
        
        # program Leader Data 
        pl_program_wise_student_count_table_data=[]
        for program in programs_for_current_user:
            program_data={
                'title':program.name,
                # 'student_count': len(program.calculate_total_no_of_student()),
                'student_count': len(set(program.calculate_total_student_enrollments())),
                'enrollment_count': len(program.calculate_total_student_enrollments())
            }
            pl_program_wise_student_count_table_data.append(program_data)
        
        
        # print("pl_program_student_count_table_data:",pl_program_student_count_table_data)
        
        total_student_enrollments=[]
        
        for program_offering in program_offerings_for_current_user:
            student_enrollment=program_offering.calculate_total_student_enrollments()
            total_student_enrollments.extend(student_enrollment)
            
        # print(f" total student enrolled {len(total_student_enrollments)} and total student count is {len(set(total_student_enrollments))}")
        
        pl_campus_wise_student_count_table_data=[]
        # Initialize a dictionary to store enrollments grouped by campus
        enrollments_by_campus = {}

        # Iterate over each student enrollment
        for student_enrollment in total_student_enrollments:
            campus_name = student_enrollment.student.campus.name
            
            # Check if the campus already exists in the dictionary
            if campus_name in enrollments_by_campus:
                # If the campus exists, append the enrollment to its list
                enrollments_by_campus[campus_name].append(student_enrollment)
            else:
                # If the campus doesn't exist, create a new list with the enrollment
                enrollments_by_campus[campus_name] = [student_enrollment]
                    
        # print("enrollments_by_campus:",enrollments_by_campus)
        for enrollment in enrollments_by_campus:
            # print("enrollment :",enrollments_by_campus[enrollment])
            enrollment_data={
                'title':enrollment,
                'student_count': len(set(enrollments_by_campus[enrollment])),    
                'enrollment_count': len(enrollments_by_campus[enrollment])  
            }
            pl_campus_wise_student_count_table_data.append(enrollment_data)
        
        # print("pl_campus_wise_student_count_table_data:",pl_campus_wise_student_count_table_data)
        
        
        # temp data for Program Leader : 
        
        campus_sample_data = [
                {
                    'title': "campus_1",
                    'student_count': 00,
                    'enrollment_count': 00
                },
                {
                    'title': "campus_2",
                    'student_count': 35,
                    'enrollment_count': 45
                },
                {
                    'title': "campus_3",
                    'student_count': 55,
                    'enrollment_count': 60
                },
                {
                    'title': "campus_4",
                    'student_count': 30,
                    'enrollment_count': 40
                },
                {
                    'title': "campus_5",
                    'student_count': 45,
                    'enrollment_count': 55
                },
                {
                    'title': "campus_6",
                    'student_count': 25,
                    'enrollment_count': 35
                },
                {
                    'title': "campus_7",
                    'student_count': 50,
                    'enrollment_count': 65
                },
                {
                    'title': "campus_8",
                    'student_count': 60,
                    'enrollment_count': 70
                },
                {
                    'title': "campus_9",
                    'student_count': 20,
                    'enrollment_count': 30
                },
                {
                    'title': "campus_10",
                    'student_count': 55,
                    'enrollment_count': 65
                }
            ]
        program_sample_data = [
                {
                    'title': "program_data",
                    'student_count': 10,
                    'enrollment_count': 10
                },
                {
                    'title': "program_2",
                    'student_count': 35,
                    'enrollment_count': 45
                },
                {
                    'title': "program_3",
                    'student_count': 55,
                    'enrollment_count': 60
                },
                {
                    'title': "program_4",
                    'student_count': 30,
                    'enrollment_count': 40
                },
                {
                    'title': "program_5",
                    'student_count': 45,
                    'enrollment_count': 55
                },
                {
                    'title': "program_6",
                    'student_count': 25,
                    'enrollment_count': 35
                },
                {
                    'title': "program_7",
                    'student_count': 50,
                    'enrollment_count': 65
                },
                {
                    'title': "program_8",
                    'student_count': 60,
                    'enrollment_count': 70
                },
                {
                    'title': "program_9",
                    'student_count': 20,
                    'enrollment_count': 30
                },
                {
                    'title': "program_10",
                    'student_count': 55,
                    'enrollment_count': 65
                }
            ]
        lecturer_sample_data = [
                {
                    'title': "lecturer_data",
                    'student_count': 20,
                    'enrollment_count': 20
                },
                {
                    'title': "lecturer_2",
                    'student_count': 35,
                    'enrollment_count': 45
                },
                {
                    'title': "lecturer_3",
                    'student_count': 55,
                    'enrollment_count': 60
                },
                {
                    'title': "lecturer_4",
                    'student_count': 30,
                    'enrollment_count': 40
                },
                {
                    'title': "lecturer_5",
                    'student_count': 45,
                    'enrollment_count': 55
                },
                {
                    'title': "lecturer_6",
                    'student_count': 25,
                    'enrollment_count': 35
                },
                {
                    'title': "lecturer_7",
                    'student_count': 50,
                    'enrollment_count': 65
                },
                {
                    'title': "lecturer_8",
                    'student_count': 60,
                    'enrollment_count': 70
                },
                {
                    'title': "lecturer_9",
                    'student_count': 20,
                    'enrollment_count': 30
                },
                {
                    'title': "lecturer_10",
                    'student_count': 55,
                    'enrollment_count': 65
                }
            ]

        context['campus_sample_data']=campus_sample_data
        pl_student_count_table_data=[
            {'title':"Campus",'data_list':pl_campus_wise_student_count_table_data},
            {'title':"Program",'data_list':pl_program_wise_student_count_table_data},
            {'title':"Lecturer",'data_list':lecturer_sample_data},
           
        ]
        
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
            }
             },
            {'program':'program 3' ,
             'attendance_percentage':{
                "present":70,
                'absent':10,
                'informed_absent':5,
                'tardy':15
            }
             },
            {
                'program': 'Program 4',
                'attendance_percentage': {
                    'present': 85,
                    'absent': 8,
                    'informed_absent': 4,
                    'tardy': 3
                }
            },
        ]
        
        context['pl_student_count_table_data']=pl_student_count_table_data
        context['program_wise_sample_attendance_data']=program_wise_sample_attendance_data
        context['attendance_choice']=ATTENDANCE_CHOICE

        # Add other necessary context data

        return context
    

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