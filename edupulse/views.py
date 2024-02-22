from typing import Any
from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from report.models import Attendance
from base.models import Campus
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
        user_data=filter_database_based_on_current_user(request_user=self.request.user)

        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
        # context.update(user_data)

        
        # filter data with start and end date
        date_filter_form = DateFilterForm(self.request.GET)
        # print("context data ",user_data['program_offerings_for_current_user'])
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date

        if date_filter_form.is_valid():
            start_date=date_filter_form.cleaned_data['start_date']
            end_date=date_filter_form.cleaned_data['end_date']

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
            context.update(filtered_data_by_date_range)
               
        context['date_filter_form']=date_filter_form




        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)



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


       
        # Check if the user has a staff_profile
        # if hasattr(self.request.user, 'staff_profile'):
        #     context['staff_profile'] = self.request.user.staff_profile
        # else:
        #     context['staff_profile'] = None

        
        context['staff_profile'] = self.request.user.staff_profile if hasattr(self.request.user, 'staff_profile') else None


        # print("current user:", self.request.user.staff_profile)
        # print("staff profile:", self.request.user.staff_profile)
    
        # Add other necessary context data

        return context
    
class ManageAttendance(LoginRequiredMixin,FormView):
    template_name='report/manage_attendance.html'
    form_class = ManageAttendanceFilterForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the request.user to the form
        return kwargs
    
    def form_valid(self, form):
        course_offering = form.cleaned_data['course_offering']
        week_number = form.cleaned_data['week_number']
        student = form.cleaned_data['student']
        start_date=course_offering.start_date + timedelta(weeks=int(week_number) - 1)
        weekly_reports=course_offering.weekly_reports.all()
        print("weekly_reports:",weekly_reports)
        weekly_report=None
        for weekly_report in weekly_reports:
                print(weekly_report.get_week_number())
                if weekly_report.get_week_number()==int(week_number):
                    print(f" week number {weekly_report.get_week_number() } and {week_number}")
                    weekly_report=weekly_report
                    print("weekly_report:",weekly_report)
        
        #  # Instantiate the form
        # form = self.get_form()
        
        # # Call the set_student_choices method to set student choices based on the selected course offering
        # form.set_student_choices(course_offering_id=self.request.POST.get('course_offering'))
        
        
        if student:
            attendance_data = Attendance.objects.filter(course_offering=course_offering, attendance_date__gte=start_date, student=student)
            # weekly_report=weekly_report.filter(student=student)
        else:
            attendance_data = Attendance.objects.filter(course_offering=course_offering, attendance_date__gte=start_date)
        
            print("final weekly_report:",weekly_report)
        return self.render_to_response(self.get_context_data(form=form, attendance_data=attendance_data,weekly_report=weekly_report))

    @method_decorator(csrf_exempt)  # Apply csrf_exempt decorator to the dispatch method
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Handle GET request to render the form initially
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        # Handle POST request to update student choices based on the selected course offering
        if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            course_offering_id = request.POST.get('course_offering_id')
            students = Student.objects.filter(course_offerings__id=course_offering_id)
            serialized_students = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name} for student in students]
            return JsonResponse(serialized_students, safe=False)
        else:
            return super().post(request, *args, **kwargs)