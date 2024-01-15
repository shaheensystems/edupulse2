from typing import Any
from django.shortcuts import render
from report.models import Attendance,WeeklyReport
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from collections import Counter
from itertools import groupby
from operator import itemgetter

from utils.function.helperGetChartData import get_chart_data_attendance_report,get_chart_data_attendance_by_date
# Create your views here.


class AttendanceListView(LoginRequiredMixin,ListView):
    model=Attendance
    template_name='attendance/attendance_list_page.html'
    context_object_name='attendances'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        weekly_reports=WeeklyReport.objects.all()
        # attendances=Attendance.objects.all()
        attendances = Attendance.objects.all().order_by('course_offering')
        attendance_by_course_offering=Counter(attendance.course_offering for attendance in attendances)


        # print(attendance_by_course_offering)
        context['attendance_by_course_offering']=attendance_by_course_offering.items()

        
        # Group attendances by course_offering
        grouped_attendances_by_course_offering = {key: list(group) for key, group in groupby(attendances, key=lambda x: x.course_offering)}
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
        return context