from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from edupulse.celery import add
from dashboard.tasks import sub,sub2

from django.http import JsonResponse
from celery.result import AsyncResult
from report.models import Attendance
from program.models import Program, ProgramOffering,Course,CourseOffering
from customUser.models import Staff, Campus
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

from utils.function.helperGetChartData import get_chart_data_attendance_report
from utils.function.helperGetTableData import (
    get_table_data_student_and_enrollment_count_by_programs,
    get_table_data_student_and_enrollment_count_by_campus_through_program_offerings,
    get_barChart_data_student_attendance_details_by_programs,
    get_barChart_data_student_at_risk_status_by_programs,
    get_barChart_data_student_by_locality_by_programs,
    get_barChart_data_student_engagement_status_by_programs,
    get_barChart_data_student_attendance_details_by_campuses,
    get_barChart_data_student_at_risk_status_by_campuses,
    get_barChart_data_student_by_locality_by_campuses,
    get_barChart_data_student_engagement_status_by_courses,
    get_table_data_student_and_enrollment_count_by_lecturer,
    get_barChart_data_student_attendance_details_by_lecturer,
    get_barChart_data_student_at_risk_status_by_lecturer,
    get_barChart_data_student_by_locality_by_lecturer,
    get_barChart_data_student_engagement_status_by_lecturer,
)
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from dashboard.filter import AttendanceEngagementReportFilter,CourseOfferingAttendanceFilterForTeacher
from django.db.models import Prefetch,Count
from django.template.loader import render_to_string
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from typing import Any

from report.models import StudentEnrollment
from django.db import connection
from utils.function.BaseValues_List import (
    ATTENDANCE_CHOICE,
    ATTENDANCE_COLOR_CHOICE,
    LOCALITY_COLOR_CHOICE,
    FINAL_STATUS_COLOR_CHOICE,
    ENGAGEMENT_COLOR_CHOICE,
)
# import logging
from django.shortcuts import get_object_or_404

# logger = logging.getLogger(__name__)
from utils.function.helperDatabaseFilter import filter_database_based_on_current_user

# Create your views here.

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name='dashboard/dashboard.html'
    
    # templateView not supported Queryset method
    def get_filtered_data(self):
        # Get the GET parameters
        date = self.request.GET.get('date')
        program_type = self.request.GET.get('program_type')
        
        print("program_type :",program_type)
        # filter data based on user logged in 
        user_data = filter_database_based_on_current_user(request_user=self.request.user)
        program_offerings_for_current_user = user_data["program_offerings_for_current_user"]
        course_offerings_for_current_user = user_data["course_offerings_for_current_user"]
        programs_for_current_user = user_data["programs_for_current_user"]
        courses_for_current_user = user_data["courses_for_current_user"]
        students = user_data["students"]
        attendances_for_current_user = user_data["attendances"]
        all_programs = user_data["all_programs"]
        weekly_reports = user_data["weekly_reports"]
        campuses = user_data["campuses"]
        lecturer_qs_for_current_user = user_data["lecturer_qs_for_current_user"]
        student_enrollments=user_data['student_enrollments']
        
        
        
        # Filter the Attendance and Program models based on the GET parameters
        # attendances = Attendance.objects.select_related('student','student__student')
        attendances = attendances_for_current_user.select_related('student','student__student')
        # connection.queries.clear()

        # Prefetch student enrollments with the related student objects
        student_enrollments_prefetch = Prefetch(
            'student_enrollments',
            queryset=StudentEnrollment.objects.select_related('student').prefetch_related('student__student')
        )
        # Prefetch program offerings with the student enrollments prefetch
        programs_for_current_user = Program.objects.prefetch_related(
            Prefetch('program_offerings', queryset=ProgramOffering.objects.prefetch_related(student_enrollments_prefetch))
        ).all()

        # or
        # programs_for_current_user = Program.objects.prefetch_related('program_offerings__student_enrollments__student')
        # Print the number of queries executed
        # print("Number of queries executed:", len(connection.queries))

        # # Print the queries to see what's being executed
        # for query in connection.queries:
        #     print(query['sql'])
       
        program_offerings_for_current_user=program_offerings_for_current_user.prefetch_related('student_enrollments__student__student__campus')
        # courses_for_current_user=Course.objects.all()
        
        if self.request.user.groups.filter(name="Program_Leader").exists() or self.request.user.groups.filter(name="Admin").exists():
            course_offerings_for_current_user=course_offerings_for_current_user
            lecturer_qs_for_current_user = lecturer_qs_for_current_user.select_related('staff').prefetch_related(
            'staff__student_profile__student_enrollments',  # Prefetch student enrollments
            'staff__student_profile__student_enrollments__course_offering',  # Prefetch course offerings
            'staff__student_profile__student_enrollments__course_offering__staff_course_offering_relations__staff',  # Prefetch related staff
            )
               
        if self.request.user.groups.filter(name="Teacher").exists():
            course_offerings_for_current_user=course_offerings_for_current_user.prefetch_related('attendances')
            
        
        
        campuses=campuses
        
        if date:
            attendances = attendances.filter(date=date)
            programs_for_current_user = programs_for_current_user.filter(date=date)
        
        if program_type:
            programs_for_current_user = programs_for_current_user.filter(type=program_type)
       
        
        total_enrollment_in_blended_course_offerings=student_enrollments.exclude(course_offering__offering_mode='online')
        total_enrollment_in_online_course_offerings=student_enrollments.filter(course_offering__offering_mode='online')
        total_students_in_blended_course_offerings = total_enrollment_in_blended_course_offerings.values_list('student', flat=True).distinct()
        total_students_in_online_course_offerings = total_enrollment_in_online_course_offerings.values_list('student', flat=True).distinct()
        
        return {
            'attendances': attendances,
            'programs_for_current_user': programs_for_current_user,
            'program_offerings_for_current_user':program_offerings_for_current_user,
            'courses_for_current_user':courses_for_current_user,
            'course_offerings_for_current_user':course_offerings_for_current_user,
            'lecturer_qs_for_current_user':lecturer_qs_for_current_user,
            'campuses':campuses,
            'total_enrollment_in_blended_course_offerings':total_enrollment_in_blended_course_offerings,
            'total_enrollment_in_online_course_offerings':total_enrollment_in_online_course_offerings,
            'total_students_in_blended_course_offerings':total_students_in_blended_course_offerings,
            'total_students_in_online_course_offerings':total_students_in_online_course_offerings,
        }
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        
        
        # Use get_filtered_data to get combined data
        filtered_data = self.get_filtered_data()
        attendances = filtered_data['attendances']
        programs_for_current_user = filtered_data['programs_for_current_user']
        program_offerings_for_current_user = filtered_data['program_offerings_for_current_user']
        lecturer_qs_for_current_user = filtered_data['lecturer_qs_for_current_user']
        course_offerings_for_current_user = filtered_data['course_offerings_for_current_user']
        courses_for_current_user = filtered_data['courses_for_current_user']
        campuses = filtered_data['campuses']
        total_enrollment_in_blended_course_offerings = filtered_data['total_enrollment_in_blended_course_offerings']
        total_enrollment_in_online_course_offerings = filtered_data['total_enrollment_in_online_course_offerings']
        total_students_in_online_course_offerings = filtered_data['total_students_in_online_course_offerings']
        total_students_in_blended_course_offerings = filtered_data['total_students_in_blended_course_offerings']
       
        
        
        
        # context data from filter function 
        # context['attendances']=attendance_data
        
        
        
        # filter forms 
       
        
        if self.request.user.groups.filter(name="Teacher").exists():
            # attendanceReportFilterForTeacher=CourseOfferingAttendanceFilterForTeacher(self.request.GET,queryset=course_offerings_for_current_user)
            # course_offerings_for_current_user=attendanceReportFilterForTeacher.qs
            # attendanceReportFilterForTeacherForm=attendanceReportFilterForTeacher.form
            # context['attendanceReportFilterForTeacherForm']=attendanceReportFilterForTeacherForm
            # Initialize the form with the current user's course offerings
            
            context['attendance_report_filter_forms'] = {
                co: CourseOfferingAttendanceFilterForTeacher(self.request.GET, queryset=co.attendances.all()).form
                for co in course_offerings_for_current_user
            }
             
             
        if self.request.user.groups.filter(name="Program_Leader").exists() or self.request.user.groups.filter(name="Admin").exists():
            
            # Generate reports
            attendance_report= self.generate_attendance_report_for_chart_data(attendances)
            student_count_table_report=self.generate_student_count_report_for_table(programs_for_current_user=programs_for_current_user, program_offerings_for_current_user=program_offerings_for_current_user,lecturer_qs_for_current_user=lecturer_qs_for_current_user,campuses=campuses)
           # set context data 
            context["chart_data_attendance_report_attendance"] = attendance_report['chart_data_attendance_report_attendance']
            context["chart_data_attendance_report_engagement"] = attendance_report['chart_data_attendance_report_engagement']
            context["chart_data_attendance_report_action"] = attendance_report['chart_data_attendance_report_action']
            context['attendanceReportFilterForm']=attendance_report['attendanceReportFilterForm']
            context["pl_student_count_table_data"] = student_count_table_report['pl_student_count_table_data']
            context["pl_campus_wise_student_count_table_data"] = student_count_table_report['pl_campus_wise_student_count_table_data']
            context["pl_student_count_button_list"] = student_count_table_report['pl_student_count_button_list']
            context["attendance_choice"] = student_count_table_report['attendance_choice']
            context["pl_campus_wise_attendance_detail_data"] = student_count_table_report['pl_campus_wise_attendance_detail_data']
            
        
        
        # common context data for all user 
        context['attendances']=attendances
        context['programs_for_current_user']=programs_for_current_user
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['lecturer_qs_for_current_user']=lecturer_qs_for_current_user
        context['course_offerings_for_current_user']=course_offerings_for_current_user
        context['courses_for_current_user']=courses_for_current_user
        context['campuses']=campuses
        context['total_enrollment_in_blended_course_offerings']=total_enrollment_in_blended_course_offerings
        context['total_enrollment_in_online_course_offerings']=total_enrollment_in_online_course_offerings
        context['total_students_in_blended_course_offerings']=total_students_in_blended_course_offerings
        context['total_students_in_online_course_offerings']=total_students_in_online_course_offerings
        return context

    
    def generate_attendance_report_for_chart_data(self, attendance_data):
        attendanceReportFilter=AttendanceEngagementReportFilter(self.request.GET,queryset=attendance_data)
        attendance_data=attendanceReportFilter.qs
        
        # Add your logic to generate the attendance report
        (
            chart_data_attendance_report_attendance,
            chart_data_attendance_report_engagement,
            chart_data_attendance_report_action,
        ) = get_chart_data_attendance_report(attendances=attendance_data)

        report = {
            'chart_data_attendance_report_attendance' :chart_data_attendance_report_attendance,
            'chart_data_attendance_report_engagement':chart_data_attendance_report_engagement,
            'chart_data_attendance_report_action':chart_data_attendance_report_action,
            'attendanceReportFilterForm':attendanceReportFilter.form
                  }
        return report

    def generate_student_count_report_for_table(self,programs_for_current_user, program_offerings_for_current_user,lecturer_qs_for_current_user,campuses):
        pl_program_wise_student_count_table_data = (
            get_table_data_student_and_enrollment_count_by_programs(
                programs=programs_for_current_user
            )
        )
       
        pl_campus_wise_student_count_table_data = (
            get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(
            program_offerings=program_offerings_for_current_user
        )
        )
        pl_lecturer_wise_student_count_table_data = (
            get_table_data_student_and_enrollment_count_by_lecturer(
                lecturer_qs=lecturer_qs_for_current_user
            )
        )
        pl_campus_wise_attendance_detail_data = (
            get_barChart_data_student_attendance_details_by_campuses(
                campuses=campuses, program_offerings=program_offerings_for_current_user
            )
        )
        
        pl_student_count_table_data = [
            {"title": "Campus", "data_list": pl_campus_wise_student_count_table_data},
            {"title": "Program", "data_list": pl_program_wise_student_count_table_data},
            {"title": "Lecturer","data_list": pl_lecturer_wise_student_count_table_data},
        ]
        pl_student_count_button_list=["Campus", "Program", "Lecturer"]
        attendance_choice = dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))
        
        
        report={
            'pl_student_count_table_data':pl_student_count_table_data,
            'pl_campus_wise_student_count_table_data':pl_campus_wise_student_count_table_data,
            'pl_campus_wise_attendance_detail_data':pl_campus_wise_attendance_detail_data,
            'pl_student_count_button_list':pl_student_count_button_list,
            'attendance_choice':attendance_choice
        }
        
        return report
    def generate_program_report(self, program_data):
        # Add your logic to generate the program report
        
        report = ...  # Replace with your logic
        return report

    def generate_combined_report(self, attendance_data, program_data):
        # Add your logic to generate the combined report
        report = ...  # Replace with your logic
        return report
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print("get request initiated ......")

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            print("get request send to ajax request handler ......")
            return self.handle_ajax_request(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)
    def handle_ajax_request(self, request, *args, **kwargs):
        # Your logic for handling AJAX request
        pl_data_table_button_id = request.GET.get("pl_data_table_button_id")

        pl_id_student_count_table_title = request.GET.get(
            "pl_id_student_count_table_title"
        )

        pl_student_count_barChart_id = request.GET.get("pl_student_count_barChart_id")
        student_count_table_title = request.GET.get("student_count_table_title")

        context = self.get_context_data(**kwargs)

        # handle pl student count data table with attendance bar chart data
        if pl_data_table_button_id:
            print("pl student count  button data get .....:",pl_data_table_button_id)
            # program_offerings_for_current_user

            if pl_data_table_button_id == "id_data_table_button_campus":
                table_button_name = "Campus"
                program_offerings_for_current_user = context.get(
                    "program_offerings_for_current_user"
                )
                campuses = context.get("campuses")
                table_data = get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(
                    program_offerings=program_offerings_for_current_user
                )
                programs_for_current_user = context.get("programs_for_current_user")
                bar_chart_attendance_data = (
                    get_barChart_data_student_attendance_details_by_campuses(
                        campuses=campuses,
                        program_offerings=program_offerings_for_current_user,
                    )
                )
                chart_title = "Campus wise Attendance - Enrollments"
            elif pl_data_table_button_id == "id_data_table_button_program":
                table_button_name = "Program"
                programs_for_current_user = context.get("programs_for_current_user")
                table_data = get_table_data_student_and_enrollment_count_by_programs(
                    programs=programs_for_current_user
                )
                bar_chart_attendance_data = (
                    get_barChart_data_student_attendance_details_by_programs(
                        programs_for_current_user
                    )
                )
                chart_title = "Program wise Attendance - Enrollments"
                print("table_data:",table_data)
            elif pl_data_table_button_id == "id_data_table_button_lecturer":
                lecturer_qs_for_current_user = context.get(
                    "lecturer_qs_for_current_user"
                )
                table_button_name = "Lecturer"
                course_offerings_for_current_user = context.get(
                    "course_offerings_for_current_user"
                )
                print("lecturer_qs_for_current_user: ",lecturer_qs_for_current_user)
                print("lecturer_qs_for_current_user: ",lecturer_qs_for_current_user)
                
                table_data = get_table_data_student_and_enrollment_count_by_lecturer(
                    lecturer_qs=lecturer_qs_for_current_user
                )
                programs_for_current_user = context.get("programs_for_current_user")
                bar_chart_attendance_data = (
                    get_barChart_data_student_attendance_details_by_lecturer(
                        lecturer_qs=lecturer_qs_for_current_user,
                        course_offerings=course_offerings_for_current_user,
                    )
                )
                chart_title = "Lecturer wise Attendance - Enrollments"
            else:
                table_button_name = ""
                table_data = []
                bar_chart_attendance_data = []
                chart_title = ""

            chart_subtitle_choice = dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))
            # Render HTML using a Django template
            html_content_student_count_table = render_to_string(
                "components/dashboard/program_leader/components/pl_student_count_table_template.html",
                {"table_button_name": table_button_name, "table_data": table_data},
            )
            html_content_student_count_barChart = render_to_string(
                "components/dashboard/program_leader/components/pl_student_count_barChart.html",
                {
                    "title": chart_title,
                    "sub_title_choice": chart_subtitle_choice,
                    "data": bar_chart_attendance_data,
                    "student_count_table_title": table_button_name,
                },
            )

            return JsonResponse(
                {
                    "html_content_table": html_content_student_count_table,
                    "html_content_barChart": html_content_student_count_barChart,
                    "status": 200,
                }
            )

        # handle pl student count bar chart data  according to table data
        if pl_student_count_barChart_id:
            table_button_name = student_count_table_title
            print(
                "initialising bar Chart data  for student count by button clicked id:",
                pl_student_count_barChart_id,
            )

            if (
                pl_student_count_barChart_id
                == "id_pl_student_count_barChart_filter_btn_attendance"
            ):
                programs_for_current_user = context.get("programs_for_current_user")
                program_offerings_for_current_user = context.get(
                    "program_offerings_for_current_user"
                )
                campuses = context.get("campuses")
                lecturer_qs_for_current_user = context.get(
                    "lecturer_qs_for_current_user"
                )
                course_offerings_for_current_user = context.get(
                    "course_offerings_for_current_user"
                )
                if table_button_name == "Campus":
                    bar_chart_data = (
                        get_barChart_data_student_attendance_details_by_campuses(
                            campuses=campuses,
                            program_offerings=program_offerings_for_current_user,
                        )
                    )
                    chart_title = "Campus wise Attendance - Enrollments"
                elif table_button_name == "Program":
                    bar_chart_data = (
                        get_barChart_data_student_attendance_details_by_programs(
                            programs_for_current_user
                        )
                    )
                    chart_title = "Program wise Attendance - Enrollments"
                elif table_button_name == "Lecturer":
                    bar_chart_data = (
                        get_barChart_data_student_attendance_details_by_lecturer(
                            lecturer_qs=lecturer_qs_for_current_user,
                            course_offerings=course_offerings_for_current_user,
                        )
                    )
                    chart_title = "Lecturer wise Attendance - Enrollments"
                else:
                    bar_chart_data = []
                    chart_title = "Student table Data not available "

                chart_subtitle_choice = dict(sorted(ATTENDANCE_COLOR_CHOICE.items()))

            elif (
                pl_student_count_barChart_id
                == "id_pl_student_count_barChart_filter_btn_final_status"
            ):
                programs_for_current_user = context.get("programs_for_current_user")
                program_offerings_for_current_user = context.get(
                    "program_offerings_for_current_user"
                )
                campuses = context.get("campuses")
                lecturer_qs_for_current_user = context.get(
                    "lecturer_qs_for_current_user"
                )
                course_offerings_for_current_user = context.get(
                    "course_offerings_for_current_user"
                )
                if table_button_name == "Campus":
                    bar_chart_data = (
                        get_barChart_data_student_at_risk_status_by_campuses(
                            campuses=campuses,
                            program_offerings=program_offerings_for_current_user,
                        )
                    )
                    chart_title = "Program wise Completion Status"
                    chart_title = "Campus wise Completion Status"
                elif table_button_name == "Program":
                    bar_chart_data = (
                        get_barChart_data_student_at_risk_status_by_programs(
                            programs_for_current_user
                        )
                    )
                    chart_title = "Program wise Completion Status"
                elif table_button_name == "Lecturer":
                    bar_chart_data = (
                        get_barChart_data_student_at_risk_status_by_lecturer(
                            lecturer_qs=lecturer_qs_for_current_user,
                            course_offerings=course_offerings_for_current_user,
                        )
                    )
                    chart_title = "Lecturer wise Completion Status"
                else:
                    bar_chart_data = []
                    chart_title = "Student table Data not available "

                chart_subtitle_choice = dict(sorted(FINAL_STATUS_COLOR_CHOICE.items()))

            elif (
                pl_student_count_barChart_id
                == "id_pl_student_count_barChart_filter_btn_locality"
            ):
                programs_for_current_user = context.get("programs_for_current_user")
                campuses = context.get("campuses")
                lecturer_qs_for_current_user = context.get(
                    "lecturer_qs_for_current_user"
                )
                course_offerings_for_current_user = context.get(
                    "course_offerings_for_current_user"
                )
                program_offerings_for_current_user = context.get(
                    "program_offerings_for_current_user"
                )
                if table_button_name == "Campus":
                    bar_chart_data = get_barChart_data_student_by_locality_by_campuses(
                        campuses=campuses,
                        program_offerings=program_offerings_for_current_user,
                    )
                    chart_title = "Campus wise Student Region"
                elif table_button_name == "Program":
                    bar_chart_data = get_barChart_data_student_by_locality_by_programs(
                        programs_for_current_user
                    )
                    chart_title = "Program wise Student Region"
                elif table_button_name == "Lecturer":
                    bar_chart_data = get_barChart_data_student_by_locality_by_lecturer(
                        lecturer_qs=lecturer_qs_for_current_user,
                        course_offerings=course_offerings_for_current_user,
                    )
                    chart_title = "Lecturer wise Student Region"
                else:
                    bar_chart_data = []
                    chart_title = "Student table Data not available "

                chart_subtitle_choice = dict(sorted(LOCALITY_COLOR_CHOICE.items()))

            elif (
                pl_student_count_barChart_id
                == "id_pl_student_count_barChart_filter_btn_engagement"
            ):
                programs_for_current_user = context.get("programs_for_current_user")
                campuses = context.get("campuses")
                program_offerings_for_current_user = context.get(
                    "program_offerings_for_current_user"
                )
                lecturer_qs_for_current_user = context.get(
                    "lecturer_qs_for_current_user"
                )
                course_offerings_for_current_user = context.get(
                    "course_offerings_for_current_user"
                )
                if table_button_name == "Campus":
                    bar_chart_data = (
                        get_barChart_data_student_engagement_status_by_courses(
                            campuses=campuses,
                            program_offerings=program_offerings_for_current_user,
                        )
                    )
                    chart_title = "Campus wise Engagement Status"
                elif table_button_name == "Program":
                    bar_chart_data = (
                        get_barChart_data_student_engagement_status_by_programs(
                            programs_for_current_user
                        )
                    )
                    chart_title = "Program wise Engagement Status"
                elif table_button_name == "Lecturer":
                    bar_chart_data = (
                        get_barChart_data_student_engagement_status_by_lecturer(
                            lecturer_qs=lecturer_qs_for_current_user,
                            course_offerings=course_offerings_for_current_user,
                        )
                    )
                    chart_title = "Lecturer wise Engagement Status"
                else:
                    bar_chart_data = []
                    chart_title = "Student table Data not available "

                chart_subtitle_choice = dict(sorted(ENGAGEMENT_COLOR_CHOICE.items()))

            else:
                bar_chart_data = []
                chart_title = ""
                chart_subtitle_choice = []

            html_content_student_count_barChart = render_to_string(
                "components/dashboard/program_leader/components/pl_student_count_barChart.html",
                {
                    "title": chart_title,
                    "sub_title_choice": chart_subtitle_choice,
                    "data": bar_chart_data,
                    "student_count_table_title": table_button_name,
                },
            )
            print("sending new barChart data to html page :")
            print(
                f" title :{chart_title}, sub title choice :{chart_subtitle_choice}, student count table title:{table_button_name} , data :{bar_chart_data}"
            )
            if html_content_student_count_barChart:
                # print("html page:",html_content_student_count_barChart)
                return JsonResponse(
                    {
                        "html_content_barChart": html_content_student_count_barChart,
                        "status": 200,
                    }
                )
            else:
                return JsonResponse(
                    {
                        "error": "Program ID not provided",
                        "message": "no data available for view ",
                    },
                    status=400,
                )

        return JsonResponse({"error": "Program ID not provided"}, status=400)


class LoadCourseOfferingDataAjaxView(View):
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        course_offering_id = kwargs.get('pk')
        
        try:
            course_offering = get_object_or_404(CourseOffering, pk=course_offering_id)
        except CourseOffering.DoesNotExist:
            return JsonResponse({'error': 'CourseOffering not found'}, status=404)
        
        session_no = self.get_cached_session_no(request)
        week_no = self.get_cached_week_no(request)
        
        calculate_student_attendance_percentage,calculate_student_attendance_chart_data = self.filter_data(course_offering=course_offering,week_no=week_no, session_no=session_no)
        
        week_and_session_no_choices=self.get_session_and_week_choices_by_course_offering(course_offering=course_offering)
        
        print("session no choice :",week_and_session_no_choices)
        
        html = render_to_string('components/dashboard/lecturer_view/course_offering_report.html', {
            'co': course_offering,
            'calculate_student_attendance_percentage':calculate_student_attendance_percentage,
            'calculate_student_attendance_chart_data':calculate_student_attendance_chart_data,
            'week_and_session_no_choices':week_and_session_no_choices,
        }, request)
        
        return JsonResponse({'html': html})
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def post(self, request, *args, **kwargs):
        course_offering_id = kwargs.get('pk')
        course_offering = get_object_or_404(CourseOffering, pk=course_offering_id)
        
       
        # Retrieve the JSON data from request.POST
        week_and_session_no_str = request.POST.get('session_no')
        
        # Parse the JSON string to a Python dictionary
        week_and_session_no = json.loads(week_and_session_no_str)
        print(" data for filter received from ajax request :",week_and_session_no)
        
        week_no=week_and_session_no['week']
        session_no=week_and_session_no['session']
        
        self.cache_session_no(request, session_no)
        self.cache_week_no(request, week_no)
        calculate_student_attendance_percentage,calculate_student_attendance_chart_data = self.filter_data(course_offering=course_offering,week_no=week_no, session_no=session_no)

        print("filter data for calculate_student_attendance_percentage:",calculate_student_attendance_percentage)
        print("filter data for calculate_student_attendance_chart_data:",calculate_student_attendance_chart_data)
        week_and_session_no_choices=self.get_session_and_week_choices_by_course_offering(course_offering=course_offering)
        
        
        html = render_to_string('components/dashboard/lecturer_view/course_offering_report.html', {
            'co': course_offering,
            'calculate_student_attendance_percentage':calculate_student_attendance_percentage,
            'calculate_student_attendance_chart_data':calculate_student_attendance_chart_data,
            'week_and_session_no_choices':week_and_session_no_choices,
        }, request)
        
        return JsonResponse({'html': html})

    def get_session_and_week_choices_by_course_offering(self,course_offering):
        week_and_session_no_choices = [
        {
        "value": {"week": attendance['week_no'], "session": attendance['session_no']},
        "text": f"Week {attendance['week_no']} : Session {attendance['session_no']}"
        }
        for attendance in course_offering.attendances.filter(course_offering__isnull=False).values('session_no', 'week_no').distinct()
        ]
        return week_and_session_no_choices
        
    def filter_data(self, course_offering,week_no, session_no):
        cache_key = f'course_offering_data_{course_offering.pk}_{week_no}_{session_no}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        if session_no is not None and week_no is not None:
            calculate_student_attendance_percentage=self.calculate_student_attendance_percentage(
            course_offering=course_offering,
            session_no=session_no,
            week_no=week_no
             )
            calculate_student_attendance_chart_data=self.calculate_student_attendance_chart_data(
                course_offering=course_offering,
                session_no=session_no,
                week_no=week_no
             )
            
        else:
            calculate_student_attendance_percentage=self.calculate_student_attendance_percentage(
            course_offering=course_offering,
            session_no=None,
            week_no=None,
             )
            calculate_student_attendance_chart_data=self.calculate_student_attendance_chart_data(
                course_offering=course_offering,
                session_no=None,
                week_no=None,
             )
        # Store calculated data in cache
        cache.set(cache_key, (calculate_student_attendance_percentage, calculate_student_attendance_chart_data), timeout=None)

        return calculate_student_attendance_percentage,calculate_student_attendance_chart_data
    
    def calculate_student_attendance_percentage(self,course_offering,session_no,week_no):
        attendances=course_offering.attendances.all()
        if session_no is not None:
            attendances=attendances.filter(session_no=session_no)
        if week_no is not None:
            attendances=attendances.filter(week_no=week_no) 
            
        present=attendances.filter(is_present='present').count()
        informed_absent=attendances.filter(is_present='informed absent').count()
        absent=attendances.filter(Q(is_present='absent')|Q(is_present='tardy')).count()
        total_attendances=attendances.count()
        if total_attendances>0 and total_attendances == present+informed_absent+absent:
            present_percentage=f'{(present / total_attendances) * 100:.2f}%'
            informed_absent_percentage=f'{(informed_absent / total_attendances) * 100:.2f}%'
            absent_percentage=f'{(absent / total_attendances) * 100:.2f}%'
        else:
            present_percentage=0
            informed_absent_percentage=0
            absent_percentage=0
            
        return{
            'present_percentage':present_percentage ,
            'informed_absent_percentage':informed_absent_percentage ,
            'absent_percentage':absent_percentage ,
        }
    def calculate_student_attendance_chart_data(self,course_offering,session_no,week_no):
        attendances=course_offering.attendances.all()
        if session_no is not None and week_no is not None:
            attendances=attendances.filter(session_no=session_no,week_no=week_no)
        
         
        if attendances:
            chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        else:
            chart_data_attendance_report_attendance=None
        return chart_data_attendance_report_attendance
    def get_cached_session_no(self, request):
        # Retrieve selected session number from cache
        return cache.get(f'selected_session_no_{request.user.id}')
    
    def get_cached_week_no(self, request):
        # Retrieve selected session number from cache
        return cache.get(f'selected_week_no_{request.user.id}')

    def cache_session_no(self, request, session_no):
        # Cache selected session number
        cache.set(f'selected_session_no_{request.user.id}', session_no, timeout=None)
        
    def cache_week_no(self, request, week_no):
        # Cache selected session number
        cache.set(f'selected_week_no_{request.user.id}', week_no, timeout=None)
        
        
class FilterAttendancesAjaxView(View):
    
   
    
    def get(self, request, *args, **kwargs):
        course_offering_id = kwargs.get('pk')
        print('course_offering_id:',course_offering_id)
        filter_instance = CourseOfferingAttendanceFilterForTeacher(
            request.GET,
            queryset=Attendance.objects.filter(course_offering_id=course_offering_id)
        )

        filtered_attendances = list(filter_instance.qs.values('id', 'session_no', 'week_no', 'attendance_date'))

        return JsonResponse({'filtered_attendances': filtered_attendances})

   
class DashboardCeleryView(LoginRequiredMixin,TemplateView):
    template_name='dashboard/dashboard_celery.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        # result=sub.apply_async(args=[20,3])
        result=sub.apply_async(kwargs={ 'y': 3,'x': 20})
        context["result"] = result
        context["task_id"] = result.id

        result_attendance_report=sub2.apply_async(kwargs={"y":17, "x":32})
        attendances=Attendance.objects.all()
        # result_attendance_report=sub2.apply_async(kwargs={"attendances":attendances})
        context['result_attendance_report']=result_attendance_report
        context['result_attendance_report_task_id']=result_attendance_report.id
        

        return context


    


def check_status_attendance_status_report_chart_data(request):
    task_id=request.GET.get('result_attendance_report_task_id')
    # task_id=request.GET.get('task_id')
    result=AsyncResult(task_id)
    response_data={
        'status':result.status,
        'result':result.result if result.successful() else None
    }
    
    return JsonResponse(response_data)
    
def check_task_status(request):
    task_id = request.GET.get('task_id')
    result = AsyncResult(task_id)
    response_data = {
        'status': result.status,
        'result': result.result if result.successful() else None
    }
    return JsonResponse(response_data)
    

