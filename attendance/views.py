from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from report.models import Attendance,WeeklyReport
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from collections import Counter
from itertools import groupby
from operator import itemgetter

from utils.function.helperGetChartData import get_chart_data_attendance_report,get_chart_data_attendance_by_date
from utils.function.helperDatabaseFilter import filter_data_based_on_date_range,default_start_and_end_date,filter_database_based_on_current_user
from customUser.models import Student
# Create your views here.


class AttendanceListView(LoginRequiredMixin,ListView):
    model=Attendance
    template_name='attendance/attendance_list_page.html'
    context_object_name='attendances'
    
    
    def get_queryset(self) :
        # return super().get_queryset()
        
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
    
        return attendances,weekly_reports,students

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        # weekly_reports=WeeklyReport.objects.all()
        # print("self object:",context['attendances'])
        
        # call attendances data from query set 
        attendances,weekly_reports,students=self.get_queryset()
        
        # weekly_reports = WeeklyReport.objects.filter(sessions__in=attendances)
        # attendances = Attendance.objects.select_related('course_offering','program_offering','student').prefetch_related().order_by('course_offering')
       
        attendance_by_course_offering=Counter(attendance.course_offering for attendance in attendances)
        # # print(attendance_by_course_offering)
        # # print(attendance_by_course_offering.items())
        # weekly_reports_from_queryset = set(weekly_reports)

        # # Get the weekly reports from the database
        # weekly_reports_from_db = set(WeeklyReport.objects.filter(sessions__in=attendances))

        # # Check if they match
        # if weekly_reports_from_queryset == weekly_reports_from_db:
        #     print("Weekly reports from queryset and database match")
        # else:
        #     print("Weekly reports from queryset and database do not match")

        # print(attendance_by_course_offering)
        context['attendance_by_course_offering']=attendance_by_course_offering.items()
        
       
       
        total_students_appear_for_attendance = attendances.values('student').distinct().count()
        context['total_students_appear_for_attendance']=total_students_appear_for_attendance
    
        
        # Group attendances by course_offering
        grouped_attendances_by_course_offering = {key: list(group) for key, group in groupby(attendances, key=lambda x: x.course_offering)}
        
        # print("grouped_attendances_by_course_offering:",grouped_attendances_by_course_offering.items())
        # Get chart data for each course_offering
        chart_data_by_course_offering = {}
        for course_offering, attendances_queryset in grouped_attendances_by_course_offering.items():
            # Ensure that attendances is a queryset
            attendances_list_query = Attendance.objects.filter(pk__in=[attendance.pk for attendance in attendances_queryset])
            chart_data_by_course_offering[course_offering] = get_chart_data_attendance_report(attendances=attendances_list_query)

        context['attendance_data_by_course_offering_for_chart'] = chart_data_by_course_offering
        context['grouped_attendances_by_course_offering'] = grouped_attendances_by_course_offering
        context['chart_data_attendance_by_date']=get_chart_data_attendance_by_date(attendances=attendances)

        

        context['weekly_reports']=weekly_reports
        
        
        
        context['attendances'] = attendances
        context['students'] = students
        context['weekly_reports'] = weekly_reports
        
        
        
        return context