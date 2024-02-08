from typing import Any
from django.shortcuts import render
from django.db.models import Count,Q
from customUser.models import Staff,Student
from report.models import Attendance
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404

from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_course_offerings,get_no_of_at_risk_students_by_program_offerings

from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,get_online_offline_program,filter_data_based_on_date_range,default_start_and_end_date,get_online_offline_courses,get_online_offline_program_offerings,get_online_offline_course_offerings
from utils.function.helperGetChartData import get_chart_data_attendance_by_date,get_chart_data_attendance_report

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_courses
from utils.function.helperAttendance import get_attendance_percentage_by_attendances

# Create your views here.

class CourseListView(LoginRequiredMixin,ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='courses'

    def get_queryset(self):
        user_data = filter_database_based_on_current_user(request_user=self.request.user)
        courses_for_current_user = user_data['courses_for_current_user']
        return courses_for_current_user
    
    def get_all_students_and_at_risk_students(self, courses):
        unique_students = set()
        no_of_at_risk_students=set()
        for course in courses:
            no_of_at_risk_students.update(get_no_of_at_risk_students_by_course_offerings(course.course_offerings.all()))
            for course_offering in course.course_offerings.all():
                unique_students.update(course_offering.student.all())

        return unique_students,no_of_at_risk_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        
        context.update(user_data)

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

        online_and_offline_courses=get_online_offline_courses(courses_for_current_user=courses_for_current_user)
        blended_courses_for_current_user=online_and_offline_courses['blended_courses_for_current_user']
        online_courses_for_current_user=online_and_offline_courses['online_courses_for_current_user']
        context.update(online_and_offline_courses)

        total_students,at_risk_students=self.get_all_students_and_at_risk_students(courses_for_current_user)
        context['total_no_of_at_risk_student'] = at_risk_students

        context['total_no_of_student_for_blended_courses']=get_total_no_of_student_by_courses(courses=blended_courses_for_current_user, offering_mode='offline')
        context['total_no_of_student_for_online_courses']=get_total_no_of_student_by_courses(courses=online_courses_for_current_user, offering_mode='online')
        context['total_no_of_student_for_all_courses']=get_total_no_of_student_by_courses(courses=blended_courses_for_current_user, offering_mode='all')
        # Add the total_students to the context
        context['total_students'] = total_students
        # Student Performance chart data 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        

        return context

class CourseDetailView(LoginRequiredMixin,DetailView):
    model=Course
    template_name='program/course/course_detail.html'
    context_object_name='course'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # You can customize the queryset here if needed
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Now you have access to self.object, which is the Course instance
        offline_students=self.object.calculate_total_no_of_student_for_offline_course()
        offline_students_attendance = Attendance.objects.filter(student__in=offline_students)
        # print(offline_students)

        context['offline_students_attendance']=offline_students_attendance
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=offline_students_attendance)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action

        return context


class ProgramListView(LoginRequiredMixin,ListView):
    model=Program
    template_name='program/program/program_list.html'
    context_object_name='programs'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        
        context.update(user_data)

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
        
        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)
        # Student Performance chart data 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action


        context['total_no_of_at_risk_student'] = get_no_of_at_risk_students_by_program_offerings(program_offerings_for_current_user)
        # Add the total_students to the context
        context['start_date']=start_date
        context['end_date']=end_date
        print(start_date,":",end_date)
        return context

class ProgramDetailView(LoginRequiredMixin,DetailView):
    model=Program
    template_name='program/program/program_detail.html'
    context_object_name='program'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offline_students=self.object.calculate_total_no_of_student_for_offline_program()
        
        blended_attendances=Attendance.objects.filter(student__in=offline_students)
        

        
         # Student Performance chart data 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=blended_attendances)
        context['blended_attendances']=blended_attendances
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action

        return context

class ProgramOfferingListView(LoginRequiredMixin,ListView):
    model=ProgramOffering
    template_name='program/program/program_offering_list.html'
    context_object_name='program_offerings'
 
   

    def get_all_students(self, program_offerings):
        unique_students = set()
        # print(program_offerings)
        for program_offering in program_offerings:
            unique_students.update(program_offering.student.all())
        
        return unique_students
    
    # def get_all_students(self, program_offerings):
    #     # Use Django's aggregation to count unique students
    #     return program_offerings.aggregate(total_students=Count('student', distinct=True))['total_students']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        default_start_date ,default_end_date=default_start_and_end_date()
        start_date = default_start_date
        end_date=default_end_date
        # user_data=filter_database_based_on_current_user(request_user=self.request.user,
        #                                                 program_offerings=ProgramOffering.objects.all(),
        #                                                 course_offerings=CourseOffering.objects.all(),
        #                                                 programs=Program.objects.all(),
        #                                                 courses=Course.objects.all(),
        #                                                 students=Student.objects.all(),
        #                                                 attendances=Attendance.objects.all()
        #                                                 )
        user_data=filter_database_based_on_current_user(request_user=self.request.user)
        program_offerings_for_current_user=user_data['program_offerings_for_current_user']
        course_offerings_for_current_user=user_data['course_offerings_for_current_user']
        programs_for_current_user=user_data['programs_for_current_user']
        courses_for_current_user=user_data['courses_for_current_user']
        students=user_data['students']
        attendances=user_data['attendances']
        all_programs=user_data['all_programs']
        weekly_reports=user_data['weekly_reports']
        
        context.update(user_data)
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
        
        
        online_and_offline_program_offerings_by_current_user = get_online_offline_program_offerings(program_offerings_for_current_user=program_offerings_for_current_user)
        
        context.update(online_and_offline_program_offerings_by_current_user)
        online_program_offerings_for_current_user=online_and_offline_program_offerings_by_current_user['online_program_offerings_for_current_user']
        blended_program_offerings_for_current_user=online_and_offline_program_offerings_by_current_user['blended_program_offerings_for_current_user']
        
        # print(program_offerings_for_current_user)
        # print("online",online_and_offline_program_offerings_by_current_user['online_program_offerings_for_current_user'])
        # print("blended",online_and_offline_program_offerings_by_current_user)
        context.update(filtered_data_by_date_range)
        # Calculate total number of students across all program offerings
        total_students_for_all_program_offerings_for_current_user = self.get_all_students(program_offerings=program_offerings_for_current_user)
        total_students_for_online_program_offerings_for_current_user = self.get_all_students(program_offerings=online_program_offerings_for_current_user)
        total_students_for_blended_program_offerings_for_current_user = self.get_all_students(program_offerings=blended_program_offerings_for_current_user)

        # Add the total_students to the context
        context['total_students_for_all_program_offerings_for_current_user'] = total_students_for_all_program_offerings_for_current_user 
        context['total_students_for_online_program_offerings_for_current_user'] = total_students_for_online_program_offerings_for_current_user 
        context['total_students_for_blended_program_offerings_for_current_user'] = total_students_for_blended_program_offerings_for_current_user  
        
        context['total_no_of_at_risk_student_by_all_program_offering_for_current_user'] = get_no_of_at_risk_students_by_program_offerings(program_offerings=program_offerings_for_current_user)
        context['total_no_of_at_risk_student_by_online_program_offering_for_current_user'] = get_no_of_at_risk_students_by_program_offerings(program_offerings=online_program_offerings_for_current_user)
        context['total_no_of_at_risk_student_by_blended_program_offering_for_current_user'] = get_no_of_at_risk_students_by_program_offerings(program_offerings=blended_program_offerings_for_current_user)

         # Student Performance chart data 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action

        return context

class ProgramOfferingDetailView(LoginRequiredMixin,DetailView):
    model = ProgramOffering
    template_name = 'program/program/program_offering_detail.html'  
    context_object_name = 'program_offering'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        
        students=self.object.student.all()
        attendances=Attendance.objects.filter(student__in=students)
       

        # Student Performance chart data 
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        context['attendances']=attendances
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
   
        return context

class CourseOfferingListView(LoginRequiredMixin,ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offerings'

    def get_all_students(self, course_offerings):
        unique_students = set()
        for course_offering in course_offerings:
            unique_students.update(course_offering.student.all())

        return unique_students

    # def get_all_students(self, course_offerings):
    #     # Use Django's aggregation to count unique students
    #     return course_offerings.aggregate(total_students=Count('student', distinct=True))['total_students']

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        
        context.update(user_data)
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

        # 6 query each function 
        online_and_offline_course_offerings_by_current_user = get_online_offline_course_offerings(course_offerings_for_current_user=course_offerings_for_current_user)
        
        context.update(online_and_offline_course_offerings_by_current_user)
        online_course_offerings_for_current_user=online_and_offline_course_offerings_by_current_user['online_course_offerings_for_current_user']
        blended_course_offerings_for_current_user=online_and_offline_course_offerings_by_current_user['blended_course_offerings_for_current_user']
       
    
    
        
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=attendances)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        
        context['total_attendance_percentage']=get_attendance_percentage_by_attendances(attendances)
        
        
        # approx 50 query on below function function 
        total_no_of_at_risk_student=get_no_of_at_risk_students_by_course_offerings(course_offerings=course_offerings_for_current_user)

        # # Add the total_students to the context
        context['total_students_for_all_course_offerings_for_current_user'] = self.get_all_students(course_offerings=course_offerings_for_current_user)
        
        # 3 query each function 
        context['total_students_for_online_course_offerings_for_current_user'] = self.get_all_students(course_offerings=online_course_offerings_for_current_user)
        context['total_students_for_blended_course_offerings_for_current_user'] = self.get_all_students(course_offerings=blended_course_offerings_for_current_user)
        
        # approx 3 query each function 
        context['total_no_of_at_risk_student_for_all_course_offerings_for_current_user'] = weekly_reports.filter(at_risk=True)
        context['total_no_of_at_risk_student_for_online_course_offerings_for_current_user'] = weekly_reports.filter(at_risk=True,course_offering__offering_mode="online")
        context['total_no_of_at_risk_student_for_blended_course_offerings_for_current_user'] = weekly_reports.filter(at_risk=True).exclude(course_offering__offering_mode = "online")

        
        
        # approx 50 query each function 
        
        # context['total_no_of_at_risk_student_for_all_course_offerings_for_current_user'] = get_no_of_at_risk_students_by_course_offerings(course_offerings=course_offerings_for_current_user)
        # context['total_no_of_at_risk_student_for_online_course_offerings_for_current_user'] = get_no_of_at_risk_students_by_course_offerings(course_offerings=online_course_offerings_for_current_user)
        # context['total_no_of_at_risk_student_for_blended_course_offerings_for_current_user'] = get_no_of_at_risk_students_by_course_offerings(course_offerings=blended_course_offerings_for_current_user)
        
        
        
        return context



class CourseOfferingDetailView(LoginRequiredMixin,DetailView):
    model = CourseOffering
    template_name = 'program/course/course_offering_detail.html'  
    context_object_name = 'course_offering'  

    def get_object(self, queryset=None):
        """
        Get the object for this view.
        """
        
        return get_object_or_404(CourseOffering, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = 'table'  # Add the 'view' context value list or detail or table

        all_attendance=context['course_offering'].attendance.all()

        # print("Attendance:",all_attendance)
        context['chart_data_attendance_by_date']=get_chart_data_attendance_by_date(attendances=all_attendance)
        chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=all_attendance)
        
        context['chart_data_attendance_report_attendance']=chart_data_attendance_report_attendance
        context['chart_data_attendance_report_engagement']=chart_data_attendance_report_engagement
        context['chart_data_attendance_report_action']=chart_data_attendance_report_action
        # print("All attendance:",all_attendance)
        return context
   


