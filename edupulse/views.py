from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from base.models import Campus
from django.views.generic import DetailView,ListView,TemplateView
from program.models import ProgramOffering,CourseOffering
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum



from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_program_offerings,get_no_of_at_risk_students_by_course_offerings

from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program_offerings,get_total_unique_no_of_student_by_program_offerings,get_total_no_of_student_by_course_offerings,get_total_unique_no_of_student_by_course_offerings

from utils.function.helperGetChartData import get_chart_data_program_offering_student_enrollment
def home(request):
    
    return render(request,'index.html')

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        program_offerings=ProgramOffering.objects.all()
        students=Student.objects.all()
        course_offerings=CourseOffering.objects.all()
        campuses=Campus.objects.all()

        # Program Offering Enrollment data for current user
        # print("current user group :",self.request.user.groups.all())
        user_groups=self.request.user.groups.all()
        if user_groups.filter(name="Head_of_School").exists() or user_groups.filter(name="Admin").exists():
            program_offerings_for_current_user=program_offerings
            course_offering_for_current_user=course_offerings
        elif user_groups.filter(name="Program_Leader").exists():
           program_offerings_for_current_user=program_offerings.filter(program_leader=self.request.user.staff_profile)
           course_offering_for_current_user=course_offerings
        elif user_groups.filter(name="Teacher").exists():
           program_offerings_for_current_user=program_offerings.filter(program__course__course_offering__teacher__staff=self.request.user)
           course_offering_for_current_user=course_offerings.filter(teacher__staff=self.request.user)
        #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
        else:
            program_offerings_for_current_user=None
            course_offering_for_current_user=None

   
       
        # print("compare st by course offerings:")
        # print(get_total_no_of_student_by_course_offerings(course_offerings=course_offerings),": here unique")
        # print(len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offerings)))
       
        # print("compare st by program offerings:")
        # print(get_total_no_of_student_by_program_offerings(program_offerings=program_offerings),":here unique")
        # print(len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings)))
       

        # print("total students :",total_students_in_program_offerings_for_current_user)

        program_offering_enrollment_data=[]
        for program_offering in program_offerings_for_current_user:
            prog_off_enrolled_students=program_offering.student.count()
            program_offering_enrollment_data.append({
                "program_name":program_offering.temp_id+":"+program_offering.program.name,
                'enrolled_students':prog_off_enrolled_students
            })
        # Sort enrollment_data based on enrolled_students in descending order
        sorted_program_offering_enrollment_data = sorted(program_offering_enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)
        
       
        program_offering_student_enrollment = {
            'labels': [enrollment['program_name'] for enrollment in sorted_program_offering_enrollment_data],
            'data': [enrollment['enrolled_students'] for enrollment in sorted_program_offering_enrollment_data],
        }
        
        # course offering enrollment data 
        enrollment_data = []
        for course_offering in course_offerings:
            enrolled_students = course_offering.student.count()
            enrollment_data.append({
                'course_name': course_offering.temp_id+":"+course_offering.course.name,
                'enrolled_students': enrolled_students,
            })
        # Sort enrollment_data based on enrolled_students in descending order
        sorted_enrollment_data = sorted(enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)

        chart_data_enrollment = {
            'labels': [enrollment['course_name'] for enrollment in sorted_enrollment_data],
            'data': [enrollment['enrolled_students'] for enrollment in sorted_enrollment_data],
        }
        campuses=Campus.objects.all()
        campus_enrollment_student=[]
        campus_enrollment_staff=[]

        for campus in campuses:
            # print("campus",campus.name)
            students_in_campus = Student.objects.filter(student__campus=campus)
            appointed_staff_in_campus=Staff.objects.filter(staff__campus=campus)
            campus_enrollment_student.append({
                'campus': campus.name,
                'students_count': students_in_campus.count(),
            })
            campus_enrollment_staff.append({
                'campus': campus.name,
                'staff_count': appointed_staff_in_campus.count(),
            })
            
        chart_data_campus_enrollment_student= {
            'labels': [enrollment['campus'] for enrollment in campus_enrollment_student],
            'data': [enrollment['students_count'] for enrollment in campus_enrollment_student],
        }
        chart_data_campus_enrollment_staff= {
            'labels': [enrollment['campus'] for enrollment in campus_enrollment_staff],
            'data': [enrollment['staff_count'] for enrollment in campus_enrollment_staff],
        }


        #Domestic and international students
        domestic_students = Student.objects.filter(international_student=False).count()
        international_students = Student.objects.filter(international_student=True).count()

        # Prepare data for the chart
        chart_data_student_region = {
            'labels': ['Domestic Students', 'International Students'],
            'data': [domestic_students, international_students],
        } 

        context['chart_data_campus_enrollment_student'] = chart_data_campus_enrollment_student
        context['chart_data_campus_enrollment_staff'] = chart_data_campus_enrollment_staff
        # context['chart_data_program_offering_student_enrollment'] = program_offering_student_enrollment
        context['chart_data_program_offering_student_enrollment'] = get_chart_data_program_offering_student_enrollment(program_offerings_for_current_user)



        context['chart_data_enrollment'] = chart_data_enrollment
        context['chart_data_student_region']=chart_data_student_region

        context['program_offerings']=program_offerings
        context['program_offerings_for_current_user']=program_offerings_for_current_user
        context['course_offerings_for_current_user']=course_offering_for_current_user
        context['total_students_in_program_offerings_for_current_user']=len(get_total_unique_no_of_student_by_program_offerings(program_offerings=program_offerings_for_current_user))
        context['total_students_in_course_offerings_for_current_user']=len(get_total_unique_no_of_student_by_course_offerings(course_offerings=course_offering_for_current_user))

        # context['total_students_in_program_offerings_for_current_user']=total_unique_students_in_program_offerings_for_current_user
        context['course_offerings']=course_offerings
        context['students']=students


        context['total_students_at_risk_query_set']=get_no_of_at_risk_students_by_program_offerings(program_offerings_for_current_user)


        # context['staff_profile'] = self.request.user.staff_profile
        # Check if the user has a staff_profile
        if hasattr(self.request.user, 'staff_profile'):
            context['staff_profile'] = self.request.user.staff_profile
        else:
            context['staff_profile'] = None

       

        # print("current user:", self.request.user.staff_profile)
        # print("staff profile:", self.request.user.staff_profile)
    
        # Add other necessary context data

        return context