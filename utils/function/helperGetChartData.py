
def get_chart_data_program_offerings_student_enrollment(program_offerings):
    program_offering_enrollment_data=[]
    for program_offering in program_offerings:
        prog_off_enrolled_students=program_offering.student.count()
        program_offering_enrollment_data.append({
            "program_name":program_offering.temp_id+":"+program_offering.program.name,
            'enrolled_students':prog_off_enrolled_students
        })
    # Sort enrollment_data based on enrolled_students in descending order
    sorted_program_offering_enrollment_data = sorted(program_offering_enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)
    
    
    chart_data_program_offerings_student_enrollment = {
        'labels': [enrollment['program_name'] for enrollment in sorted_program_offering_enrollment_data],
        'data': [enrollment['enrolled_students'] for enrollment in sorted_program_offering_enrollment_data],
    }

    return chart_data_program_offerings_student_enrollment


def get_chart_data_course_offerings_student_enrollment(course_offerings):
    enrollment_data = []
    for course_offering in course_offerings:
        enrolled_students = course_offering.student.count()
        enrollment_data.append({
            'course_name': course_offering.temp_id+":"+course_offering.course.name,
            'enrolled_students': enrolled_students,
        })
    # Sort enrollment_data based on enrolled_students in descending order
    sorted_enrollment_data = sorted(enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)

    chart_data_course_offerings_student_enrollment = {
        'labels': [enrollment['course_name'] for enrollment in sorted_enrollment_data],
        'data': [enrollment['enrolled_students'] for enrollment in sorted_enrollment_data],
    }
    return chart_data_course_offerings_student_enrollment


def get_chart_data_student_and_Staff_by_campus():
    from customUser.models import Student,Staff
    from base.models import Campus
    campus_list=Campus.objects.all()
    campus_enrollment_student=[]
    campus_enrollment_staff=[]

    for campus in campus_list:
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
        
    chart_data_student_enrollment_by_campus= {
        'labels': [enrollment['campus'] for enrollment in campus_enrollment_student],
        'data': [enrollment['students_count'] for enrollment in campus_enrollment_student],
    }
    chart_data_staff_enrollment_by_campus= {
        'labels': [enrollment['campus'] for enrollment in campus_enrollment_staff],
        'data': [enrollment['staff_count'] for enrollment in campus_enrollment_staff],
    }

    return chart_data_student_enrollment_by_campus,chart_data_staff_enrollment_by_campus


def get_chart_data_student_enrollment_by_region(students):
     #Domestic and international students
    domestic_students = students.filter(international_student=False).count()
    international_students = students.filter(international_student=True).count()

    # Prepare data for the chart
    chart_data_student_region = {
        'labels': ['Domestic Students', 'International Students'],
        'data': [domestic_students, international_students],
    } 

    return chart_data_student_region

