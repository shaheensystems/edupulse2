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
    
    # print(f"By Program  Enrollment count:{len(enrollment_list)} and student count :{len(set(enrollment_list))} ")
    return table_data_student_and_enrollment_count_by_programs


def get_table_data_student_and_enrollment_count_by_campus_through_program_offerings(program_offerings):
    total_student_enrollments=[]
    if program_offerings:
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

def get_table_data_student_and_enrollment_count_by_lecturer(lecturer_qs):
    table_data_student_and_enrollment_count_by_campus_through_course_offerings=[]
    for lecturer in lecturer_qs:
        # print("Enrolled Students:",data['enrolled_students'])
        lecturer_name = lecturer.staff.first_name +" "+ lecturer.staff.last_name
        enrollment_data={
            'title':lecturer,
            'student_count':  len(set(lecturer.calculate_total_student_enrolled())),     
            'enrollment_count': len(lecturer.calculate_total_student_enrolled())
        }
        
        table_data_student_and_enrollment_count_by_campus_through_course_offerings.append(enrollment_data)
        
    return table_data_student_and_enrollment_count_by_campus_through_course_offerings
    

# helper function to get sorted  attendance percentage by cat "present, absent, informed absent and tardy "

def get_sorted_attendance_percentage_by_cat_through_students(students):
    from report.models import Attendance
    students=set(students)
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
    
    return attendance_status, sorted_attendance_percentage

def get_barChart_data_student_attendance_details_by_lecturer(lecturer_qs,course_offerings):
    table_data_student_attendance_details_by_lecturer=[]
    for lecturer in lecturer_qs:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        # enrolled_students=lecturer.calculate_total_student_enrolled()
        enrolled_students=lecturer.calculate_total_student_enrolled().filter(student_enrollments__course_offering__in=course_offerings)
        
        students=set(enrolled_students)
        attendance_status,sorted_attendance_percentage = get_sorted_attendance_percentage_by_cat_through_students(students=students)
        lecturer_name = lecturer.staff.first_name +" "+ lecturer.staff.last_name
        # print(" lecturer_name:",lecturer_name)
        table_data_student_attendance_details_by_lecturer.append(
            
                {
                'data':lecturer,
                'status':attendance_status,
                'percentage':sorted_attendance_percentage
                }
            )
        # print(" table_data_student_attendance_details_by_lecturer:",table_data_student_attendance_details_by_lecturer)
    return table_data_student_attendance_details_by_lecturer

def get_barChart_data_student_attendance_details_by_campuses(campuses,program_offerings):
    table_data_student_attendance_details_by_campuses=[]
    for campus in campuses:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        # enrolled_students=campus.calculate_total_student_enrolled().filter(student_enrollments__program_offering__in=program_offerings)
        if program_offerings is not None:
            enrolled_students = campus.calculate_total_student_enrolled().filter(student_enrollments__program_offering__in=program_offerings)
        else:
            # Handle the case when program_offerings is None
            from customUser.models import Student
            enrolled_students = Student.objects.none()
        
        
        students=set(enrolled_students)
        
        attendance_status,sorted_attendance_percentage = get_sorted_attendance_percentage_by_cat_through_students(students=students)
            
        table_data_student_attendance_details_by_campuses.append(
                {
                'data':campus,
                'status':attendance_status,
                'percentage':sorted_attendance_percentage
                }
            )
    return table_data_student_attendance_details_by_campuses

def get_barChart_data_student_attendance_details_by_programs(programs):
    table_data_student_attendance_details_by_programs=[]
    for program in programs:

        students =set(program.calculate_total_student_enrollments())
        attendance_status,sorted_attendance_percentage = get_sorted_attendance_percentage_by_cat_through_students(students=students)
        
        table_data_student_attendance_details_by_programs.append(
                {
                'data':program,
                'status':attendance_status,
                'percentage':sorted_attendance_percentage
                }
            )
    return table_data_student_attendance_details_by_programs

def get_sorted_at_risk_status_through_students(students):
    from report.models import WeeklyReport
    weekly_reports=WeeklyReport.objects.select_related('student').filter(student__in=students).distinct()
            
            
    weekly_report_count=weekly_reports.values('at_risk').annotate(at_risk_count=Count('at_risk'))
    total_weekly_reports=weekly_reports.count()
    # print('weekly_report_count:',weekly_report_count)
    # print('total_weekly_reports:',total_weekly_reports)
    
    weekly_report_percentage={}
    weekly_report_status=False
    for weekly_report in weekly_report_count:
        weekly_report_cat=weekly_report['at_risk']
        if weekly_report_cat == True:
            weekly_report_cat = 'at risk'
        elif weekly_report_cat == False:
            weekly_report_cat = 'on track'
        else:
            weekly_report_cat = 'unknown'
            
            
        count=weekly_report['at_risk_count']
        if count>0:
            weekly_report_status=True
        percentage=(count*100)/total_weekly_reports
        weekly_report_percentage[weekly_report_cat]="{:.2%}".format(percentage/100)
    sorted_weekly_report_percentage=dict(sorted(weekly_report_percentage.items()))
    return weekly_report_status,sorted_weekly_report_percentage

def get_barChart_data_student_at_risk_status_by_lecturer(lecturer_qs,course_offerings):
    table_data_student_at_risk_status_by_lecturer=[]
    for lecturer in lecturer_qs:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=lecturer.calculate_total_student_enrolled().filter(student_enrollments__course_offering__in=course_offerings)
        
        students=set(enrolled_students)
        weekly_report_status,sorted_weekly_report_percentage= get_sorted_at_risk_status_through_students(students=students)
            
        table_data_student_at_risk_status_by_lecturer.append(
                    {
                    'data':lecturer,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
    return table_data_student_at_risk_status_by_lecturer

def get_barChart_data_student_at_risk_status_by_campuses(campuses,program_offerings):
    table_data_student_at_risk_status_by_campuses=[]
    for campus in campuses:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=campus.calculate_total_student_enrolled().filter(student_enrollments__program_offering__in=program_offerings)
        
        students=set(enrolled_students)
        weekly_report_status,sorted_weekly_report_percentage= get_sorted_at_risk_status_through_students(students=students)
            
        table_data_student_at_risk_status_by_campuses.append(
                    {
                    'data':campus,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
    return table_data_student_at_risk_status_by_campuses

def get_barChart_data_student_at_risk_status_by_programs(programs):
    table_data_student_at_risk_status_by_programs=[]
    for program in programs:
            from report.models import WeeklyReport
            
            students =set(program.calculate_total_student_enrollments())
            weekly_report_status,sorted_weekly_report_percentage=get_sorted_at_risk_status_through_students(students=students)
           
                
            table_data_student_at_risk_status_by_programs.append(
                    {
                    'data':program,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
            # print(table_data_student_at_risk_status_by_programs)
    return table_data_student_at_risk_status_by_programs


def get_sorted_student_by_locality_through_students(students_set):
    from customUser.models import Student   
    # convert into query set for use filter
    students = Student.objects.filter(id__in=[student.id for student in students_set])

    students_count=students.values('international_student').annotate(international_student_count=Count('international_student'))
    # print("student Count:",students_count)
    total_students_count=students.count()
    students_count_percentage={}
    students_status=False
    for students in students_count:
        students_cat=students['international_student']
        if students_cat == True:
            students_cat="international"
        elif students_cat == False:
            students_cat="domestic"
        else :
            students_cat="unknown"
        count=students['international_student_count']
        if count >0:
            students_status=True
        percentage=(count*100)/total_students_count
        students_count_percentage[students_cat]="{:.2%}".format(percentage/100)
        
    sorted_student_count_percentage=dict(sorted(students_count_percentage.items()))  
    
    return students_status,sorted_student_count_percentage

def get_barChart_data_student_by_locality_by_programs(programs):
    table_data_student_by_locality_by_programs=[]
    for program in programs:
       
            students_set =set(program.calculate_total_student_enrollments())
            
            students_status,sorted_student_count_percentage=get_sorted_student_by_locality_through_students(students_set=students_set)

            table_data_student_by_locality_by_programs.append(
                    {
                    'data':program,
                    'status':students_status,
                    'percentage':sorted_student_count_percentage
                    }
                )
            # print(table_data_student_by_locality_by_programs)
    return table_data_student_by_locality_by_programs

def get_barChart_data_student_by_locality_by_lecturer(lecturer_qs,course_offerings):
    table_data_student_by_locality_by_lecturer=[]
    for lecturer in lecturer_qs:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=lecturer.calculate_total_student_enrolled().filter(student_enrollments__course_offering__in=course_offerings)
        
        students_set=set(enrolled_students)
        students_status,sorted_student_count_percentage=get_sorted_student_by_locality_through_students(students_set=students_set)
   
        table_data_student_by_locality_by_lecturer.append(
                    {
                    'data':lecturer,
                    'status':students_status,
                    'percentage':sorted_student_count_percentage
                    }
                )
    return table_data_student_by_locality_by_lecturer

def get_barChart_data_student_by_locality_by_campuses(campuses,program_offerings):
    table_data_student_by_locality_by_campuses=[]
    for campus in campuses:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=campus.calculate_total_student_enrolled().filter(student_enrollments__program_offering__in=program_offerings)
        
        students_set=set(enrolled_students)
        students_status,sorted_student_count_percentage=get_sorted_student_by_locality_through_students(students_set=students_set)
   
        table_data_student_by_locality_by_campuses.append(
                    {
                    'data':campus,
                    'status':students_status,
                    'percentage':sorted_student_count_percentage
                    }
                )
    return table_data_student_by_locality_by_campuses

def get_sorted_student_by_engagement_through_students(students_set):
    from report.models import WeeklyReport
    students=students_set
    weekly_reports=WeeklyReport.objects.select_related('student').filter(student__in=students).distinct()
    weekly_report_count=weekly_reports.values('engagement').annotate(engagement_count=Count('engagement'))
    total_weekly_reports=weekly_reports.count()
    # print('weekly_report_count:',weekly_report_count)
    # print('total_weekly_reports:',total_weekly_reports)
    
    weekly_report_percentage={}
    weekly_report_status=False
    for weekly_report in weekly_report_count:
        weekly_report_cat=weekly_report['engagement']
       
        count=weekly_report['engagement_count']
        if count>0:
            weekly_report_status=True
        percentage=(count*100)/total_weekly_reports
        weekly_report_percentage[weekly_report_cat]="{:.2%}".format(percentage/100)
    sorted_weekly_report_percentage=dict(sorted(weekly_report_percentage.items()))
    return weekly_report_status, sorted_weekly_report_percentage


def get_barChart_data_student_engagement_status_by_programs(programs):
    table_data_student_engagement_status_by_programs=[]
    for program in programs:
            students_set =set(program.calculate_total_student_enrollments())
            weekly_report_status, sorted_weekly_report_percentage=get_sorted_student_by_engagement_through_students(students_set)
            table_data_student_engagement_status_by_programs.append(
                    {
                    'data':program,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
            # print('table_data_student_engagement_status_by_programs:',table_data_student_engagement_status_by_programs)
    return table_data_student_engagement_status_by_programs

def get_barChart_data_student_engagement_status_by_courses(campuses,program_offerings):
    table_data_student_engagement_status_by_campuses=[]
    for campus in campuses:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=campus.calculate_total_student_enrolled().filter(student_enrollments__program_offering__in=program_offerings)
        
        students_set=set(enrolled_students)
        weekly_report_status, sorted_weekly_report_percentage=get_sorted_student_by_engagement_through_students(students_set)
   
        table_data_student_engagement_status_by_campuses.append(
                    {
                    'data':campus,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
    return table_data_student_engagement_status_by_campuses

def get_barChart_data_student_engagement_status_by_lecturer(lecturer_qs,course_offerings):
    table_data_student_engagement_status_by_lecturer=[]
    for lecturer in lecturer_qs:
        
        # student_enrollments=campus.calculate_total_student_enrollments().filter(users__student_profile__student_enrollments__program_offering__in=program_offerings)    
        enrolled_students=lecturer.calculate_total_student_enrolled().filter(student_enrollments__course_offering__in=course_offerings)
        
        students_set=set(enrolled_students)
        weekly_report_status, sorted_weekly_report_percentage=get_sorted_student_by_engagement_through_students(students_set)
   
        table_data_student_engagement_status_by_lecturer.append(
                    {
                    'data':lecturer,
                    'status':weekly_report_status,
                    'percentage':sorted_weekly_report_percentage
                    }
                )
    return table_data_student_engagement_status_by_lecturer

