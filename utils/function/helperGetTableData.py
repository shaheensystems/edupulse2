def get_table_data_student_and_enrollment_count_by_programs(programs):
    table_data_student_and_enrollment_count_by_programs=[]
    for program in programs:
        program_data={
            'title':program.name,
            # 'student_count': len(program.calculate_total_no_of_student()),
            'student_count': len(set(program.calculate_total_student_enrollments())),
            'enrollment_count': len(program.calculate_total_student_enrollments())
        }
        table_data_student_and_enrollment_count_by_programs.append(program_data)
    
    return table_data_student_and_enrollment_count_by_programs


def get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(program_offerings):
    total_student_enrollments=[]
        
    for program_offering in program_offerings:
        student_enrollment=program_offering.calculate_total_student_enrollments()
        total_student_enrollments.extend(student_enrollment)
    
    table_data_student_and_enrollment_count_by_campus_through_program_offerings=[]
        # Initialize a dictionary to store enrollments grouped by campus
    enrollments_by_campus = {}

    # Iterate over each student enrollment
    for student_enrollment in total_student_enrollments:
        campus_name = student_enrollment.student.campus.name
        
        # Check if the campus already exists in the dictionary
        if campus_name in enrollments_by_campus:
            # If the campus exists, append the enrollment to its list
            enrollments_by_campus[campus_name].append(student_enrollment)
        else:
            # If the campus doesn't exist, create a new list with the enrollment
            enrollments_by_campus[campus_name] = [student_enrollment]
                
    # print("enrollments_by_campus:",enrollments_by_campus)
    for enrollment in enrollments_by_campus:
        # print("enrollment :",enrollments_by_campus[enrollment])
        enrollment_data={
            'title':enrollment,
            'student_count': len(set(enrollments_by_campus[enrollment])),    
            'enrollment_count': len(enrollments_by_campus[enrollment])  
        }
        table_data_student_and_enrollment_count_by_campus_through_program_offerings.append(enrollment_data)
    
    return table_data_student_and_enrollment_count_by_campus_through_program_offerings