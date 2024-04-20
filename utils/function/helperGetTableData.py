from django.db.models import Q,F,Count

def get_table_data_student_and_enrollment_count_by_programs(programs):
    table_data_student_and_enrollment_count_by_programs=[]
    enrollment_list=[]
    for program in programs:
        program_data={
            'title':program.name,
            # 'student_count': len(program.calculate_total_no_of_student()),
            'student_count': len(set(program.calculate_total_student_enrollments())),
            'enrollment_count': len(program.calculate_total_student_enrollments())
        }
        enrollment_list.extend(program.calculate_total_student_enrollments())
        
        table_data_student_and_enrollment_count_by_programs.append(program_data)
    
    print(f"By Program  Enrollment count:{len(enrollment_list)} and student count :{len(set(enrollment_list))} ")
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

def get_table_data_student_and_enrollment_count_by_course_offerings(course_offerings):
 
    
    table_data_student_and_enrollment_count_by_campus_through_course_offerings=[]   
    enrollment_list=[]
    for course_offering in course_offerings:
  
        student_enrollment=course_offering.calculate_total_student_enrollments()
        enrollment_list.extend(student_enrollment)
        student_enrollment_list=student_enrollment
        
        unique_student_list = set(student_enrollment)
        
        enrollment_data={
            'title':course_offering,
            # 'student_count': len(enrollments_by_course_offerings[course_offering]),    
            'student_count': len(unique_student_list),    
            'enrollment_count': len(student_enrollment_list)  
        }
        table_data_student_and_enrollment_count_by_campus_through_course_offerings.append(enrollment_data)
    
    
    print(f"By Course offering   Enrollment count:{len(enrollment_list)} and student count :{len(set(enrollment_list))} ")
    return table_data_student_and_enrollment_count_by_campus_through_course_offerings

def get_table_data_student_and_enrollment_count_by_lecturer_through_course_offerings(course_offerings):
    # print(f"student count by course offerings: {get_table_data_student_and_enrollment_count_by_course_offerings(course_offerings)}")
    table_data_student_and_enrollment_count_by_campus_through_course_offerings=[]
    lecturer_data=[]

    for course_offering in course_offerings:
        lecturer_objs=course_offering.staff_course_offering_relations.all()
        lecturer_name_list=[]
        for lecturer in lecturer_objs:
            lecturer_name=lecturer.staff.staff.first_name+" "+lecturer.staff.staff.last_name
            lecturer_name_list.append(lecturer_name)
            # [{lecturer_1},{lecturer_2}]
            
        # print(f"lecturer name :{lecturer_name_list}")
        
        student_enrollment=course_offering.calculate_total_student_enrollments()
        # print(f"Student Enrollment from course offering : {student_enrollment}")
        # Convert the list to a tuple before using it as a key
        lecturer_name_tuple = tuple(lecturer_name_list)
        
        # Check if the lecturer already exists in the lecturer_data list
        lecturer_exists = False
        
        for lecturer in lecturer_data:
            if lecturer['name'] == lecturer_name_tuple:
                lecturer['enrolled_students'].extend(student_enrollment)
                # print("enrolled students :",lecturer['enrolled_students'])
                lecturer_exists = True
                break
        
        if not lecturer_exists:
            data = {
                "name": lecturer_name_tuple,
                "enrolled_students": student_enrollment
            }
            lecturer_data.append(data)
    
    for data in lecturer_data:
        # print("Enrolled Students:",data['enrolled_students'])
        enrollment_data={
            'title':data['name'],
            'student_count':  len(set(data['enrolled_students'])),     
            'enrollment_count': len(data['enrolled_students'])
        }
        
        table_data_student_and_enrollment_count_by_campus_through_course_offerings.append(enrollment_data)
    # print(table_data_student_and_enrollment_count_by_campus_through_course_offerings)
    
    
    
    
    return table_data_student_and_enrollment_count_by_campus_through_course_offerings


def get_table_data_student_attendance_details_by_programs(programs):
    table_data_student_attendance_details_by_programs=[]
    for program in programs:
            from report.models import Attendance
            
            students =set(program.calculate_total_student_enrollments())
            
            attendances=Attendance.objects.select_related('student').filter(student__in =students).distinct()
            attendance_counts = attendances.values('is_present').annotate(count=Count('is_present'))
            
            total_attendance=attendances.count()
            
            attendance_percentage={}
            
            attendance_status=False
            
            for attendance_count in attendance_counts:
                attendance_cat= attendance_count['is_present']
                # if attendance_cat=='informed absent':
                #     attendance_cat="informed_absent"
                count=attendance_count['count']
                if count>0:
                    attendance_status=True
                percentage=(count*100)/total_attendance
                attendance_percentage[attendance_cat]="{:.2%}".format(percentage/100)
            
            sorted_attendance_percentage = dict(sorted(attendance_percentage.items()))
                
            table_data_student_attendance_details_by_programs.append(
                    {
                    'data':program,
                    'status':attendance_status,
                    'percentage':sorted_attendance_percentage
                    }
                )
    return table_data_student_attendance_details_by_programs