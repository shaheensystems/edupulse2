from program.models import Program,Course,ProgramOffering,CourseOffering
from report.models import Attendance
from customUser.models import Student
from django.db.models import Q
from datetime import datetime, timedelta

def filter_database_based_on_current_user(request_user,program_offerings, course_offerings, programs, courses, students,attendances):
    user_groups=request_user.groups.all()
    
  

    if user_groups.filter(name="Head_of_School").exists() or user_groups.filter(name="Admin").exists():
        program_offerings_for_current_user=program_offerings
        course_offerings_for_current_user=course_offerings
        programs_for_current_user=programs
        courses_for_current_user=courses
        students=students
        all_programs=programs

        attendances = attendances.filter(student__in=students)
    elif user_groups.filter(name="Program_Leader").exists():
        program_offerings_for_current_user=program_offerings.filter(program_leader=request_user.staff_profile)
        course_offerings_for_current_user=course_offerings.filter(course__program__program_offerings__program_leader=request_user.staff_profile)
        students=students.filter(program_offering__program_leader__staff=request_user)
        
        programs_for_current_user=None
        courses_for_current_user=None
        attendances = attendances.filter(student__in=students)
        all_programs=programs_for_current_user
        # print(attendances)
        # print(students)
    elif user_groups.filter(name="Teacher").exists():
        program_offerings_for_current_user=program_offerings.filter(program__course__course_offering__teacher__staff=request_user)
        course_offerings_for_current_user=course_offerings.filter(teacher__staff=request_user)
        students=students.filter(course_offerings__teacher__staff=request_user)
        programs_for_current_user=None
        courses_for_current_user=None
        attendances = attendances.filter(student__in=students)
        all_programs=programs_for_current_user
    #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
    else:
        program_offerings_for_current_user=None
        course_offerings_for_current_user=None
        programs_for_current_user=None
        courses_for_current_user=None
        students=None
        attendances = None
        all_programs=programs_for_current_user
     # Return the filtered data
    return {
        'program_offerings_for_current_user': program_offerings_for_current_user,
        'course_offerings_for_current_user': course_offerings_for_current_user,
        'programs_for_current_user': programs_for_current_user,
        'courses_for_current_user': courses_for_current_user,
        'students': students,
        'attendances': attendances,
        'all_programs': all_programs,
        
    }

def get_online_offline_program(programs_for_current_user):
    if programs_for_current_user is not None:
                        online_programs_for_current_user=programs_for_current_user.filter(
                                        Q(program_offerings__offering_mode="online")
                                    )
                        offline_programs_for_current_user=programs_for_current_user.filter(
                                    ~Q(program_offerings__offering_mode="online")
                        )
    else:
            online_programs_for_current_user=None      
            offline_programs_for_current_user=None                                      
    return {
           'online_programs_for_current_user':online_programs_for_current_user,
           'offline_programs_for_current_user':offline_programs_for_current_user
           }

def default_start_and_end_date():
    # default_start_date = datetime.now() - timedelta(days=365)  # One year ago
    default_start_date = datetime(datetime.now().year - 1, 1, 1).strftime('%Y-%m-%d')  # 1st Jan of lst year
    default_end_date=datetime.now().strftime('%Y-%m-%d')
    return default_start_date,default_end_date

def filter_data_based_on_date_range(start_date,end_date,programs_for_current_user,courses_for_current_user,program_offerings_for_current_user,course_offerings_for_current_user,attendances):
    default_start_date ,default_end_date=default_start_and_end_date()
    if not start_date:
        start_date = default_start_date
    if not end_date:
        end_date=default_end_date

    # filter data according to start and end date 
    if start_date and end_date:

        if program_offerings_for_current_user is not None :
            program_offerings_for_current_user=program_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
        if course_offerings_for_current_user is not None :
            course_offerings_for_current_user=course_offerings_for_current_user.filter(start_date__gte=start_date,end_date__lte=end_date)
        
        # all program and course need to be shown 
        if programs_for_current_user is not None:

            active_programs = programs_for_current_user.filter(
                                                            Q(program_offerings__start_date__gte=start_date) &
                                                            Q(program_offerings__end_date__lte=end_date)
                                                        ).distinct()
            # Get the inactive programs (programs that do not match the date criteria)
            inactive_programs = programs_for_current_user.exclude(id__in=active_programs.values_list('id', flat=True))
            
            programs_for_current_user = active_programs
            active_programs_for_current_user = active_programs

            inactive_programs_for_current_user=inactive_programs
            # print(len(programs_for_current_user))
            # print(len(inactive_programs_for_current_user))
            

        if courses_for_current_user is not None:
            courses_for_current_user = courses_for_current_user.filter(
                                                            Q(course_offering__start_date__gte=start_date) &
                                                            Q(course_offering__end_date__lte=end_date)
                                                        ).distinct()
        
        
        if attendances is not None:
            attendances=attendances.filter(
                Q(attendance_date__gte=start_date)&
                Q(attendance_date__lte=end_date)
            ).distinct()

    return {
         'program_offerings_for_current_user': program_offerings_for_current_user,
        'course_offerings_for_current_user': course_offerings_for_current_user,
        'programs_for_current_user': programs_for_current_user,
        'courses_for_current_user': courses_for_current_user,
        'active_programs_for_current_user': active_programs_for_current_user,
        'inactive_programs_for_current_user': inactive_programs_for_current_user,
        'attendances': attendances,
    }
