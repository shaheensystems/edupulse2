
def get_chart_data_program_offering_student_enrollment(program_offerings):
    program_offering_enrollment_data=[]
    for program_offering in program_offerings:
        prog_off_enrolled_students=program_offering.student.count()
        program_offering_enrollment_data.append({
            "program_name":program_offering.temp_id+":"+program_offering.program.name,
            'enrolled_students':prog_off_enrolled_students
        })
    # Sort enrollment_data based on enrolled_students in descending order
    sorted_program_offering_enrollment_data = sorted(program_offering_enrollment_data, key=lambda x: x['enrolled_students'], reverse=True)
    
    
    chart_data_program_offering_student_enrollment = {
        'labels': [enrollment['program_name'] for enrollment in sorted_program_offering_enrollment_data],
        'data': [enrollment['enrolled_students'] for enrollment in sorted_program_offering_enrollment_data],
    }

    return chart_data_program_offering_student_enrollment