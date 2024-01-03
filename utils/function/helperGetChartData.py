
def get_chart_data_offering_type_student_enrollment(course_offerings):
    
    offering_type_data=[]
    for course_offering in course_offerings:
        offering_type = course_offering.offering_mode.title()

        # Check if offering_type is already present in offering_type_data
        existing_entry = next((entry for entry in offering_type_data if entry["offering_type"] == offering_type), None)

        if existing_entry:
            # If offering_type is found, update the total_students count
            existing_entry["total_students"].update(course_offering.student.all())
        else:
            # If offering_type is not found, add a new entry
            offering_type_data.append({
                "offering_type": offering_type,
                "total_students":set(course_offering.student.all())
            })

    # Sort enrollment_data based on enrolled_students in descending order
    
    sorted_offering_type_enrollment_data = sorted(offering_type_data, key=lambda x: x['offering_type'], reverse=True)
    # set1=set()
    # set2=set()
    # set3=set()
    # set4=set()
    
    # for enrollment in sorted_offering_type_enrollment_data:
    #     if enrollment['offering_type']=='blended':
    #         set1.update(enrollment['total_students'])
    #     elif enrollment['offering_type']=='online':
    #         set2.update(enrollment['total_students'])
    #     elif enrollment['offering_type']=='micro cred':
    #         set3.update(enrollment['total_students'])
    #     else:
    #         set4=set(enrollment['total_students'])
    
    # print("set value 1:",len(set1))
    # print("set value 2:",len(set2))
    # print("set value 3:",len(set3))
    # print("set value 4:",len(set4))
    # combined_set = set1.union(set2, set3, set4)
    # common_values_set1_set2 = set1.intersection(set2)
    # common_values_set1_set3 = set1.intersection(set3)
    # common_values_set2_set3 = set2.intersection(set3)

    # print("Common Values in Set1 and Set2:", len(common_values_set1_set2))
    # print("Common Values in Set1 and Set3:", len(common_values_set1_set3))
    # print("Common Values in Set2 and Set3:", len(common_values_set2_set3))
    # print("total Students :",len(set1)+len(set2)+len(set3)+len(set4))
    # print("total Students :",len(combined_set))



    chart_data_course_offering_mode_student_enrollment = {
        'labels': [enrollment['offering_type'] for enrollment in sorted_offering_type_enrollment_data],
        'data': [len(enrollment['total_students']) for enrollment in sorted_offering_type_enrollment_data],
    }
    
    return chart_data_course_offering_mode_student_enrollment

def get_chart_data_programs_student_enrollment(programs):
    if programs:
        programs_enrollment_data=[]
        for program in programs:
            programs_enrolled_students=program.calculate_total_no_of_student()
            programs_enrollment_data.append({
                # "program_name":program.temp_id+":"+program.name,
                "program_name":program.temp_id,
                'enrolled_students':programs_enrolled_students
            })
        # Sort enrollment_data based on enrolled_students in descending order
        sorted_programs_enrollment_data = sorted(programs_enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)
        
        
        chart_data_programs_student_enrollment = {
            'labels': [enrollment['program_name'] for enrollment in sorted_programs_enrollment_data],
            'data': [enrollment['enrolled_students'] for enrollment in sorted_programs_enrollment_data],
        }

        return chart_data_programs_student_enrollment

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

