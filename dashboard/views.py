from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from edupulse.celery import add
from dashboard.tasks import sub,sub2

from django.http import JsonResponse
from celery.result import AsyncResult
from report.models import Attendance
from program.models import Program, ProgramOffering,Course,CourseOffering
from customUser.models import Staff, Campus
import json
from django.core.serializers.json import DjangoJSONEncoder

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

from dashboard.filter import AttendanceEngagementReportFilter
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

# Create your views here.

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name='dashboard/dashboard.html'
    
    # templateView not supported Queryset method
    def get_filtered_data(self):
        # Get the GET parameters
        date = self.request.GET.get('date')
        program_type = self.request.GET.get('program_type')
        
        # Filter the Attendance and Program models based on the GET parameters
        attendance_data = Attendance.objects.select_related('student','student__student')
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
       
        program_offerings_for_current_user=ProgramOffering.objects.prefetch_related('student_enrollments__student__student__campus')
        courses_for_current_user=Course.objects.all()
        course_offerings_for_current_user=CourseOffering.objects.all()
        lecturer_qs_for_current_user = Staff.objects.select_related('staff').prefetch_related(
            'staff__student_profile__student_enrollments',  # Prefetch student enrollments
            'staff__student_profile__student_enrollments__course_offering',  # Prefetch course offerings
            'staff__student_profile__student_enrollments__course_offering__staff_course_offering_relations__staff',  # Prefetch related staff
        )
        
        campuses=Campus.objects.all()
        if date:
            attendance_data = attendance_data.filter(date=date)
            programs_for_current_user = programs_for_current_user.filter(date=date)
        
        if program_type:
            programs_for_current_user = programs_for_current_user.filter(type=program_type)
        
        return {
            'attendance_data': attendance_data,
            'programs_for_current_user': programs_for_current_user,
            'program_offerings_for_current_user':program_offerings_for_current_user,
            'courses_for_current_user':courses_for_current_user,
            'course_offerings_for_current_user':course_offerings_for_current_user,
            'lecturer_qs_for_current_user':lecturer_qs_for_current_user,
            'campuses':campuses,
        }
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        
        
        # Use get_filtered_data to get combined data
        filtered_data = self.get_filtered_data()
        attendance_data = filtered_data['attendance_data']
        programs_for_current_user = filtered_data['programs_for_current_user']
        program_offerings_for_current_user = filtered_data['program_offerings_for_current_user']
        lecturer_qs_for_current_user = filtered_data['lecturer_qs_for_current_user']
        course_offerings_for_current_user = filtered_data['course_offerings_for_current_user']
        courses_for_current_user = filtered_data['courses_for_current_user']
        campuses = filtered_data['campuses']
        
        
        # context data from filter function 
        # context['attendances']=attendance_data
        
        
        
        # filter forms 
        
        context['attendances']=attendance_data
        
        # Generate reports
        attendance_report= self.generate_attendance_report_for_chart_data(attendance_data)
        student_count_table_report=self.generate_student_count_report_for_table(programs_for_current_user=programs_for_current_user, program_offerings_for_current_user=program_offerings_for_current_user,lecturer_qs_for_current_user=lecturer_qs_for_current_user,campuses=campuses)
        

        
        # set context data 
        context["chart_data_attendance_report_attendance"] = attendance_report['chart_data_attendance_report_attendance']
        context["chart_data_attendance_report_engagement"] = attendance_report['chart_data_attendance_report_engagement']
        context["chart_data_attendance_report_action"] = attendance_report['chart_data_attendance_report_action']
        context['attendanceReportFilterForm']=attendance_report['attendanceReportFilterForm']
        
        context['program_report'] = self.generate_program_report(programs_for_current_user)
        context['combined_report'] = self.generate_combined_report(attendance_data, programs_for_current_user)
        
        context["pl_student_count_table_data"] = student_count_table_report['pl_student_count_table_data']
        context["pl_campus_wise_student_count_table_data"] = student_count_table_report['pl_campus_wise_student_count_table_data']
        context["pl_student_count_button_list"] = student_count_table_report['pl_student_count_button_list']
        context["attendance_choice"] = student_count_table_report['attendance_choice']
        context["pl_campus_wise_attendance_detail_data"] = student_count_table_report['pl_campus_wise_attendance_detail_data']
        context['programs_for_current_user']=programs_for_current_user
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['lecturer_qs_for_current_user']=lecturer_qs_for_current_user
        context['course_offerings_for_current_user']=course_offerings_for_current_user
        context['courses_for_current_user']=courses_for_current_user
        context['campuses']=campuses
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
    

