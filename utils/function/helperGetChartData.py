from collections import Counter
from report.models import WeeklyReport
from datetime import datetime,timedelta
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

def get_chart_data_attendance_report(attendances):
    attendance_data=[]
    engagement_data=[]
    action_data=[]
    chart_data_attendance_report_attendance={}
    chart_data_attendance_report_engagement={}
    chart_data_attendance_report_action={}
    # print(attendances)
    if attendances:
        absent_attendances_only=attendances.exclude(is_present='present')
        weekly_reports_absent_students=WeeklyReport.objects.filter(sessions__in=absent_attendances_only)
        weekly_reports_absent_students_not_engaged=weekly_reports_absent_students.filter(engagement='not engaged')
        # print("student count for attendance report all:",attendances.count())
        # print("student count for attendance report engagement:",absent_attendances_only.count())
        # print("student count for attendance report action:",weekly_reports_absent_students_not_engaged.count())
   
   
        is_present_counts=Counter(attendance.is_present for attendance in attendances)
        engagement_counts=Counter(weekly_report.engagement for weekly_report in weekly_reports_absent_students)
        action_counts=Counter(weekly_report.action for weekly_report in weekly_reports_absent_students_not_engaged)
        
    # for wr in weekly_reports_absent_students:
    #     # print(wr.engagement,":",wr.engagement,":",wr.student)
    #     if wr.engagement=='na':
    #         print(wr.week_number,":" ,wr.engagement ,":",wr.action,":",wr.student)
    #         for attendance in wr.sessions.all():
    #            print( attendance.attendance_date)

        for is_present , count in is_present_counts.items():
            attendance_data.append({
                'attendance_type':is_present,
                'attendance_count':count
            })

        for engagement , count in engagement_counts.items():
            engagement_data.append({
                'engagement_type':engagement,
                'engagement_count':count
            })

        for action , count in action_counts.items():
            # print("actions:",action)
            action_data.append({
                'action_type':action,
                'action_count':count
            })

        chart_data_attendance_report_attendance={
            'labels':[attendance['attendance_type'] for attendance in attendance_data],
            'data':[attendance['attendance_count'] for attendance in attendance_data], 
        }
        chart_data_attendance_report_engagement={
            'labels':[engagement['engagement_type'] for engagement in engagement_data],
            'data':[engagement['engagement_count'] for engagement in engagement_data],
        }


        chart_data_attendance_report_action={
            'labels':[action['action_type'] for action in action_data],
            'data':[action['action_count'] for action in action_data],
        }

    return chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action


def get_chart_data_attendance_by_date(attendances):

    attendance_data=[]
   

    attendance_count={}
    for attendance in attendances:
        
        attendance_date=attendance.attendance_date

        existing_date=next((item for item in attendance_data if item['date'] == attendance_date),None)
        # Check if the date is already in attendance_data
        if existing_date is None:
            attendance_data.append({'date':attendance_date,"total_attendance" : 0,"total_present" : 0})
        
        for item in attendance_data:
            if item['date'] == attendance_date:
                item['total_attendance'] += 1
                if attendance.is_present == 'present':
                    item['total_present'] += 1

        
        for item in attendance_data:
            item['attendance_percentage']= (item['total_present']/item['total_attendance'])*100
    
    # print(attendance_data)   
    
    sorted_attendance_data=sorted(attendance_data,key=lambda x:x['date'],reverse=True)
    labels=[item['date'].strftime("%Y-%m-%d") for item in sorted_attendance_data]
    data=[item["attendance_percentage"] for item in sorted_attendance_data]
 
    chart_data_attendance_by_date={
        'labels': labels,
        'data': data,
        "chart_type":"bar"
    }
    return chart_data_attendance_by_date