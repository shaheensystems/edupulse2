from django.shortcuts import render, redirect
from customUser.models import Student,Staff
from base.models import Campus
from django.views.generic import DetailView,ListView,TemplateView
from program.models import ProgramOffering,CourseOffering
from django.contrib.auth.mixins import LoginRequiredMixin



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
            print("campus",campus.name)
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

   
       
        context['chart_data_campus_enrollment_student'] = chart_data_campus_enrollment_student
        context['chart_data_campus_enrollment_staff'] = chart_data_campus_enrollment_staff
        context['chart_data_enrollment'] = chart_data_enrollment
        context['program_offerings']=program_offerings
        context['course_offerings']=course_offerings
        context['students']=students

        # Add other necessary context data

        return context