from django.shortcuts import render
from django.db.models import Count,Q
from customUser.models import Staff,Student
from report.models import Attendance
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from django.utils import timezone

from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_course_offerings,get_no_of_at_risk_students_by_program_offerings
from utils.function.helperDatabaseFilter import filter_database_based_on_current_user,get_online_offline_program
# Create your views here.

class CourseListView(LoginRequiredMixin,ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='courses'

    def get_all_students_and_at_risk_students(self, courses):
        unique_students = set()
        no_of_at_risk_students=set()
        for course in courses:
            no_of_at_risk_students.update(get_no_of_at_risk_students_by_course_offerings(course.course_offering.all()))
            for course_offering in course.course_offering.all():
                unique_students.update(course_offering.student.all())

        return unique_students,no_of_at_risk_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_offerings=CourseOffering.objects.all()
        courses=Course.objects.all()
        total_students,at_risk_students=self.get_all_students_and_at_risk_students(courses)
        context['total_no_of_at_risk_student'] = at_risk_students
        # Add the total_students to the context
        context['total_students'] = total_students
        

        return context

class CourseDetailView(LoginRequiredMixin,DetailView):
    model=Course
    template_name='program/course/course_detail.html'
    context_object_name='course'



class ProgramListView(LoginRequiredMixin,ListView):
    model=Program
    template_name='program/program/program_list.html'
    context_object_name='programs'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        
        context.update(user_data)

        # program_offerings=ProgramOffering.objects.all()
        # programs=Program.objects.all()
        # total_students=0
        # for programs in programs:
        #     total_students+=programs.calculate_total_no_of_student()
        # # Calculate total number of students across all program offerings
        # calculated online and offline program after all filter, search and query
        online_and_offline_programs=get_online_offline_program(programs_for_current_user=programs_for_current_user)
        context.update(online_and_offline_programs)
        
        context['total_no_of_at_risk_student'] = get_no_of_at_risk_students_by_program_offerings(program_offerings_for_current_user)
        # Add the total_students to the context
       

        return context

class ProgramDetailView(LoginRequiredMixin,DetailView):
    model=Program
    template_name='program/program/program_detail.html'
    context_object_name='program'

class ProgramOfferingListView(LoginRequiredMixin,ListView):
    model=ProgramOffering
    template_name='program/program/program_offering_list.html'
    context_object_name='program_offerings'
 
    def get_queryset(self):
        user = self.request.user
        # print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return ProgramOffering.objects.all()

        # Check if the user is a teacher
        elif user.groups.filter(name='Teacher').exists():
            # print("condition matched for teacher")
            # return CourseOffering.objects.filter(course__program__program_offerings__program_leader__staff=user)  
            # Teacher has no access for program 
            # return ProgramOffering.objects.filter(program__course__course_offering__staff=user)
            return ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)

        elif user.groups.filter(name='Program_Leader').exists():
            # return ProgramOffering.objects.none()
            return ProgramOffering.objects.filter(program_leader__staff=user)  
        
        elif user.groups.filter(name='Student').exists():
            return ProgramOffering.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        else:
            return ProgramOffering.objects.none()

    def get_all_students(self, program_offerings):
        unique_students = set()
        # print(program_offerings)
        for program_offering in program_offerings:
            unique_students.update(program_offering.student.all())
        
        return unique_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        program_offerings = context['program_offerings']
        
        # Calculate total number of students across all program offerings
        total_students = self.get_all_students(program_offerings)

        # Add the total_students to the context
        context['total_students'] = len(total_students)   
        context['total_no_of_at_risk_student'] = get_no_of_at_risk_students_by_program_offerings(program_offerings)
        context['current_user'] = self.request.user

        return context

class ProgramOfferingDetailView(LoginRequiredMixin,DetailView):
    model = ProgramOffering
    template_name = 'program/program/program_offering_detail.html'  
    context_object_name = 'program_offering'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        # Assuming 'performance' is a field in the WeeklyReport model
        courses = self.object.program.course.all()  # Adjust the related name accordingly
        course_offering_count=0
        for course in courses:
            
            for course_offering in course.course_offering.all():
                course_offering_count+=1
              

        # context['poor_performance_data'] = poor_performance_data
        context['total_course_offering_count']=course_offering_count
   
        return context

class CourseOfferingListView(LoginRequiredMixin,ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offerings'
    
    # print("initialise Course Offering view :")
    def get_queryset(self):
        user = self.request.user
        # print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return CourseOffering.objects.all()

        # Check if the user is a teacher
        elif user.groups.filter(name='Teacher').exists():
            # print("condition matched for teacher")
            # Assuming there is a ForeignKey from CourseOffering to Teacher model
            # only course offering where teacher is equal to current user
            return CourseOffering.objects.filter(teacher__staff=user)
        elif user.groups.filter(name='Program_Leader').exists():

            return CourseOffering.objects.filter(course__program__program_offerings__program_leader__staff=user)  
        
        elif user.groups.filter(name='Student').exists():
            return CourseOffering.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return CourseOffering.objects.none()
    
    
 
    def get_all_students(self, course_offerings):
        unique_students = set()
        for course_offering in course_offerings:
            unique_students.update(course_offering.student.all())

        return unique_students

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        course_offerings = context['course_offerings']
        
        # Calculate total number of students across all program offerings
        total_students = self.get_all_students(course_offerings)
        total_no_of_at_risk_student=get_no_of_at_risk_students_by_course_offerings(course_offerings=course_offerings)

        # Add the total_students to the context
        context['total_students'] = len(total_students)
        context['total_no_of_at_risk_student'] = len(total_no_of_at_risk_student)

        return context

class CourseOfferingDetailView(LoginRequiredMixin,DetailView):
    model = CourseOffering
    template_name = 'program/course/course_offering_detail.html'  
    context_object_name = 'course_offering'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = 'table'  # Add the 'view' context value list or detail or table

        all_attendance=context['course_offering'].attendance.all()
        # Create a dictionary to store attendance count date-wise
        attendance_count = {}

        # Iterate through each attendance record
        for attendance in all_attendance:
            # Get the attendance date
            date = attendance.attendance_date
            # print("Date :",date)

            # If the date is not in the dictionary, add it
            if date not in attendance_count:
                attendance_count[date] = 0

            # Update the attendance count based on the 'is_present' value
            if attendance.is_present == 'present':
                attendance_count[date] += 1
    
        # Extract the labels and data for the chart
        labels = list(attendance_count.keys())
        data = list(attendance_count.values())

        formatted_labels = [date.strftime("%Y-%m-%d") for date in labels]
        # set initial value 0 and empty to get a good chart view 
        formatted_labels.insert(0, "")
        data.insert(0, 0)   
        # print("labels :",formatted_labels)       

        # Add the labels and data to the context
        context['chart_data_attendance'] = {
            'labels': formatted_labels,
            'data': data,
            'current_user' : self.request.user,
        }

        # print("All attendance:",all_attendance)
        return context
   


