from django.shortcuts import render
from django.db.models import Count,Q
from customUser.models import Staff
from django.views.generic import ListView,DetailView,UpdateView,CreateView
from program.models import Course,CourseOffering,Program,ProgramOffering
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from django.utils import timezone
# Create your views here.

class CourseListView(LoginRequiredMixin,ListView):
    model=Course
    template_name='program/course/course_list.html'
    context_object_name='course'

class CourseDetailView(LoginRequiredMixin,DetailView):
    model=Course
    template_name='program/course/course_detail.html'
    context_object_name='course'



class ProgramListView(LoginRequiredMixin,ListView):
    model=Program
    template_name='program/program/program_list.html'
    context_object_name='programs'

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
        print("user group :",user.groups.all())
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
    
    # print(context_object_name)
    
    # def get_all_students(self, program_offerings):
    #     student_count = 0
    #     for program_offering in program_offerings:
                # chances of duplicate students
    #         student_count += program_offering.student.all().count()
    #     return student_count
    def get_all_students(self, program_offerings):
        unique_students = set()
        print(program_offerings)
        for program_offering in program_offerings:
            unique_students.update(program_offering.student.all())
        
        return unique_students

        # get at_risk Students here 

        return unique_students
    # this code is correct 4 result 
    def get_no_of_at_risk_student(self,program_offerings):
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        
        program_offerings=ProgramOffering.objects.all()
        for program_offering in program_offerings:

            program=program_offering.program
            courses = program.course.all()

            # Initialize variable to track the count of at-risk students
            at_risk_students = set()
            
            # Get all students associated with the course offering
           
            # Iterate over each course to accumulate session counts
            for course in courses:
                # Get all CourseOfferings associated with the current course and program offering
                course_offerings = course.course_offering.all()

                # Iterate over each CourseOffering to handle potential multiple objects
                for course_offering in course_offerings:
                    students=course_offering.student.all()
                    # Iterate over each student to check their at-risk status for the last week
                    # for student in students:
                    #     # print("studnet :",student)
                    #     # Check if there is a weekly report for the student and course offering in the last week
                    #     weekly_report_last_week = WeeklyReport.objects.filter(
                    #         student=student,
                    #         course_offering=course_offering,
                    #         sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                    #     ).first()
                    #     # print("weekly report found ",weekly_report_last_week)
                    #     # If there is a weekly report, check if the student is at risk
                    #     if weekly_report_last_week and weekly_report_last_week.at_risk:
                    #         # print("at _risk status on week report found in PO",student.temp_id)
                    #         at_risk_students.add(student)
                    #         # print("all object PO",at_risk_students)
                    for student in students:
                            all_weekly_reports_last_week = WeeklyReport.objects.filter(
                                    student=student,
                                    course_offering=course_offering,
                                    sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                                )
                                    
                            if all_weekly_reports_last_week:
                                for weekly_report in  all_weekly_reports_last_week:
                                    if weekly_report.at_risk is True:
                                        at_risk_students.add(student)

        return at_risk_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        program_offerings = context['program_offerings']
        
        # Calculate total number of students across all program offerings
        total_students = self.get_all_students(program_offerings)
        total_no_of_at_risk_student=self.get_no_of_at_risk_student(program_offerings)
        # Add the total_students to the context
        context['total_students'] = len(total_students)   
        context['total_no_of_at_risk_student'] = total_no_of_at_risk_student

        return context

class ProgramOfferingDetailView(LoginRequiredMixin,DetailView):
    model = ProgramOffering
    template_name = 'program/program/program_offering_detail.html'  
    context_object_name = 'program_offering'  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Assuming 'performance' is a field in the WeeklyReport model
        courses = self.object.program.course.all()  # Adjust the related name accordingly
        # print("All course",courses)
        # Dictionary to store poor performance count for each course
        poor_performance_data = []

        for course in courses:
            # print("Each Course",course)
            # print("for each course get all course_offering :",course.course_offering.all().count())
            for course_offering in course.course_offering.all():
                weekly_reports = course_offering.weekly_reports.values('week_number').annotate(
                total=Count('pk'),
                # poor_performance=Count('pk', filter=Q(performance='poor'))
                )

                for report in weekly_reports:
                    week_number = report['week_number']
                    total_count = report['total']
                    # poor_count = report['poor_performance']

                     # Create a dictionary for each course offering and week
                    offering_data = {
                    'course_offering': course_offering,
                    'week_number': week_number,
                    'total_students': total_count,
                    # 'poor_performance_count': poor_count,
                    }

                    # poor_performance_data.append(offering_data)

        # context['poor_performance_data'] = poor_performance_data
        context['total_course_offering_count']=course.course_offering.all().count()
        return context

class CourseOfferingListView(LoginRequiredMixin,ListView):
    model=CourseOffering
    template_name='program/course/course_offering_list.html'
    context_object_name='course_offerings'
    
    print("initialise Course Offering view :")
    def get_queryset(self):
        user = self.request.user
        # print("user group :",user.groups.all())
        # Check if the user is an admin
        if user.groups.filter(name='Admin').exists() or user.groups.filter(name='Head_of_School').exists():
            # print("condition matched admin")
            return CourseOffering.objects.all()

        # Check if the user is a teacher
        elif user.groups.filter(name='Teacher').exists():
            print("condition matched for teacher")
            # Assuming there is a ForeignKey from CourseOffering to Teacher model
            # only course offering where teacher is equal to current user
            return CourseOffering.objects.filter(teacher__staff=user)
        elif user.groups.filter(name='Program_Leader').exists():

            return CourseOffering.objects.filter(course__program__program_offerings__program_leader__staff=user)  
        
        elif user.groups.filter(name='Student').exists():
            return CourseOffering.objects.none()
        # For other user groups (e.g., students), return an empty queryset
        return CourseOffering.objects.none()
    
    print(context_object_name)
 
    def get_all_students(self, course_offerings):
        unique_students = set()

        for course_offering in course_offerings:
            unique_students.update(course_offering.student.all())

        return unique_students

    
     #  get all students at_risk  
    #  wrong code total 3 result 1 result missing 
    def get_no_of_at_risk_student(self, course_offerings):
        from report.models import WeeklyReport
        current_date = datetime.now().date()

        # Calculate the start and end dates for the last week
        end_date_last_week = current_date - timedelta(days=current_date.weekday() + 1)
        start_date_last_week = end_date_last_week - timedelta(days=6)
        # print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)

        # Initialize variable to track the count of at-risk students
        at_risk_students = set()
         # Get all students associated with the course offering

         # Get all courses associated with the course offerings
        course_offerings = course_offerings

        for course_offering in course_offerings:

            # for student in course_offering.student.all():
            #             #  not found this id incorrect  total 3 result 
            #             # if student.temp_id=="2020769":
            #             #     print("weekly Report at risk count dates :,",start_date_last_week," to ",end_date_last_week)
            #             #     print("id Matched",student.temp_id)
            #             # print("studnet :",student)
            #             # Check if there is a weekly report for the student and course offering in the last week
            #             weekly_report_last_week = WeeklyReport.objects.filter(
            #                 student=student,
            #                 course_offering=course_offering,
            #                 sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
            #             ).first()
            #             # print("weekly report found ",weekly_report_last_week)
            #             # If there is a weekly report, check if the student is at risk
            #             if weekly_report_last_week and weekly_report_last_week.at_risk:
            #                 # print("at _risk status on week report found in CO",student.temp_id)
            #                 at_risk_students.add(student)
            #                 # print("all object CO",at_risk_students)
                        
            #                 # print("is id  Matched added or not ",student.temp_id)
            for student in course_offering.student.all():
                            all_weekly_reports_last_week = WeeklyReport.objects.filter(
                                    student=student,
                                    course_offering=course_offering,
                                    sessions__attendance_date__range=[start_date_last_week, end_date_last_week]
                                )
                                    
                            if all_weekly_reports_last_week:
                                for weekly_report in  all_weekly_reports_last_week:
                                    if weekly_report.at_risk is True:
                                        at_risk_students.add(student)
        return at_risk_students
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # send filtred data according to user group 
        course_offerings = context['course_offerings']
        
        # Calculate total number of students across all program offerings
        total_students = self.get_all_students(course_offerings)
        total_no_of_at_risk_student=self.get_no_of_at_risk_student(course_offerings)
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
        print("labels :",formatted_labels)       

        # Add the labels and data to the context
        context['chart_data_attendance'] = {
            'labels': formatted_labels,
            'data': data,
        }

        print("All attendance:",all_attendance)
        return context
   


