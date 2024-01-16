from program.models import Program,Course,ProgramOffering,CourseOffering
from report.models import Attendance
from customUser.models import Student

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