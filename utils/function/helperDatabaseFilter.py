from program.models import Program, Course, ProgramOffering, CourseOffering
from report.models import Attendance, WeeklyReport
from customUser.models import Student, Staff
from base.models import Campus
from django.db.models import Q
from datetime import datetime, timedelta
from django.db.models import Count, Prefetch


def filter_database_based_on_current_user(request_user):
    user_groups = request_user.groups.all()
    programs = Program.objects.prefetch_related(
        "courses",
        "program_offerings",
        "program_offerings__student",
        "program_offerings__program_leader",
        "program_offerings__student__attendances",
        "program_offerings__student__attendances__weekly_reports",
        "program_offerings__program__courses",
        "program_offerings__program__courses__course_offerings",
        "program_offerings__program__courses__course_offerings__attendances",
        "program_offerings__program__courses__course_offerings__student",
        "program_offerings__program__courses__course_offerings__student__attendances",
        "program_offerings__program__courses__course_offerings__student__attendances__weekly_reports",
        "program_offerings__program__program_offerings",
        "program_offerings__program__courses__course_offerings__weekly_reports",
        "program_offerings__staff_program_offering_relations",
        "program_offerings__staff_program_offering_relations__staff",
        "program_offerings__attendances",
        "program_offerings__attendances__weekly_reports",
        "program_offerings__attendances__weekly_reports__sessions__program_offering",
        "program_offerings__attendances__weekly_reports__sessions__course_offering",
        "program_offerings__attendances__weekly_reports__sessions__student",
        "program_offerings__attendances__weekly_reports__student",
        "program_offerings__student__attendances__weekly_reports__sessions",
        "program_offerings__student_enrollments__student",
        "program_offerings__student_enrollments__course_offering",
        "program_offerings__staff_program_offering_relations__staff__staff",
        "courses__course_offerings",
        "courses__course_offerings__teacher",
        "courses__course_offerings__course__program",
        "courses__course_offerings__course__program__program_offerings",
        "courses__program",
        "courses__program__program_offerings",
        "courses__course_offerings__staff_course_offering_relations",
        "courses__course_offerings__staff_course_offering_relations__staff",
        "courses__course_offerings__student_enrollments__student",
        "courses__course_offerings__student",
        "courses__course_offerings__weekly_reports",
    ).all()
    courses = Course.objects.prefetch_related("course_offerings", "program").all()
    program_offerings = (
        ProgramOffering.objects.select_related(
            "program",
        )
        .prefetch_related(
            "student",
            "program_leader",
            "student__attendances",
            "student__attendances__weekly_reports",
            "program__courses",
            "program__courses__course_offerings",
            "program__courses__course_offerings__attendances",
            "program__courses__course_offerings__student",
            "program__courses__course_offerings__student__attendances",
            "program__courses__course_offerings__student__attendances__weekly_reports",
            "program__program_offerings",
            "program__courses__course_offerings__weekly_reports",
            "staff_program_offering_relations",
            "staff_program_offering_relations__staff",
            "attendances",
            "attendances__weekly_reports",
            "student__attendances__weekly_reports",
            "student_enrollments__student",
            "student_enrollments__student__student__campus",
            "student_enrollments__course_offering",
            "student_enrollments__course_offering__student_enrollments",
            "student_enrollments__course_offering__student_enrollments__student__student",
            "staff_program_offering_relations__staff__staff",
        )
        .all()
    )

    course_offerings = (
        CourseOffering.objects.select_related("course")
        .prefetch_related(
            "student",
            "teacher",
            "course__program",
            "course__program__program_offerings",
            "staff_course_offering_relations",
            "staff_course_offering_relations__staff",
            "student_enrollments__student",
            "student_enrollments__student__student",
            # Prefetch('attendance', queryset=Attendance.objects.filter(is_present='present'), to_attr='present_attendance'),
            # Prefetch('attendance', queryset=Attendance.objects.exclude(is_present='present'), to_attr='absent_attendance')
        )
        .all()
    )
    # programs=Program.objects.all(),
    # courses=Course.objects.all(),
    students = (
        Student.objects.select_related("student", "student__campus")
        .prefetch_related(
            "attendances",
            "attendances__course_offering",
            "course_offerings",
            "course_offerings__course",
            "course_offerings__course__program",
            "program_offering",
            "program_offering__program",
            "program_offering__student_enrollments",
            "student_enrollments",
            "student_enrollments__course_offering",
            "student_enrollments__program_offering",
            "student_enrollments__program_offering__student",
            "weekly_reports",
            "weekly_reports__sessions",
        )
        .all()
    )
    attendances = (
        Attendance.objects.select_related(
            "course_offering", "program_offering", "student"
        )
        .prefetch_related("weekly_reports")
        .all()
    )
    weekly_reports = (
        WeeklyReport.objects.select_related("course_offering", "student")
        .prefetch_related(
            "student__attendances",
            "student__student_enrollments__course_offering",
            "student__student_enrollments__program_offering",
            "course_offering__student_enrollments",
            "course_offering__student_enrollments__student",
            "course_offering__course__program__program_offerings",
            "sessions",
            "sessions__course_offering__course__program",
        )
        .all()
    )

    campuses = Campus.objects.prefetch_related(
        "users", "users__student_profile__student_enrollments__course_offering"
    )
    lecturer = Staff.objects.select_related("staff").prefetch_related(
        "staff_course_offering_relations",
        "staff_program_offering_relations",
        "staff_program_relations",
        "staff_course_offering_relations__course_offering",
        "staff_program_offering_relations__program_offering",
        "staff_program_relations__program",
    )

    if (
        user_groups.filter(name="Head_of_School").exists()
        or user_groups.filter(name="Admin").exists()
    ):
        program_offerings = program_offerings
        course_offerings = course_offerings
        students = students
        # attendances=Attendance.objects.all()
        attendances = attendances
        campuses = campuses
        # attendances=Attendance.objects.select_related('student','course_offering').all()

        program_offerings_for_current_user = program_offerings
        course_offerings_for_current_user = course_offerings
        programs_for_current_user = programs
        courses_for_current_user = courses
        students = students
        all_programs = program_offerings_for_current_user
        lecturer_qs_for_current_user = lecturer

        attendances = (
            attendances.select_related("course_offering", "program_offering", "student")
            .prefetch_related("weekly_reports")
            .order_by("course_offering")
            .filter(student__in=students)
            .distinct()
        )
        weekly_reports = weekly_reports.filter(
            course_offering__in=course_offerings_for_current_user
        ).distinct()

        # print("Query :",program_offerings_for_current_user.query)
    elif user_groups.filter(name="Program_Leader").exists():
        program_offerings = program_offerings
        course_offerings = course_offerings
        students = students
        attendances = attendances
        # campuses=campuses

        # programs_for_current_user=None
        programs_for_current_user = programs.filter(
            staff_program_relations__staff__staff=request_user
        )
        courses_for_current_user = None

        # program_offerings_for_current_user=program_offerings.filter(staff_program_offering_relations__staff__staff=request_user)
        program_offerings_for_current_user = program_offerings.filter(
            program__in=programs_for_current_user
        ).distinct()

        course_offerings_for_current_user = course_offerings.filter(
            course__program__program_offerings__in=program_offerings_for_current_user
        ).distinct()

        lecturer_qs_for_current_user = lecturer.filter(
            staff_course_offering_relations__course_offering__in=course_offerings_for_current_user
        ).distinct()

        students = students.filter(
            student_enrollments__course_offering__in=course_offerings_for_current_user
        ).distinct()
        # students=students.filter(student_enrollments__program_offering__in=program_offerings_for_current_user).distinct()

        attendances = (
            attendances.order_by("course_offering")
            .filter(course_offering__in=course_offerings_for_current_user)
            .distinct()
        )

        campuses = campuses.filter(
            users__student_profile__student_enrollments__course_offering__in=course_offerings_for_current_user
        ).distinct()

        all_programs = programs_for_current_user
        weekly_reports = weekly_reports.filter(
            course_offering__in=course_offerings_for_current_user
        ).distinct()
        # print("initialise  program for program leader ",programs_for_current_user)
        # print("initialise  course offerings  for program leader ",course_offerings_for_current_user)

        # print(attendances)
        # print(students)
    elif user_groups.filter(name="Teacher").exists():
        program_offerings = program_offerings
        course_offerings = course_offerings
        students = students
        attendances = attendances
        campuses = campuses
        lecturer_qs_for_current_user = None
        program_offerings_for_current_user = program_offerings.filter(
            staff_program_offering_relations__staff__staff=request_user
        )
        course_offerings_for_current_user = course_offerings.filter(
            staff_course_offering_relations__staff__staff=request_user
        )
        # students=students.filter(course_offerings__teacher__staff=request_user)

        students = students.filter(
            course_offerings__staff_course_offering_relations__staff__staff=request_user
        )

        programs_for_current_user = None
        courses_for_current_user = None
        # attendances = attendances.filter(student__in=students)
        attendances = (
            attendances.order_by("course_offering")
            .filter(student__in=students)
            .distinct()
        )

        all_programs = program_offerings_for_current_user
        weekly_reports = weekly_reports.filter(
            course_offering__in=course_offerings_for_current_user
        ).distinct()

    #    ProgramOffering.objects.filter(program__course__course_offering__teacher__staff=user)
    else:
        program_offerings_for_current_user = None
        course_offerings_for_current_user = None
        programs_for_current_user = None
        courses_for_current_user = None
        students = None
        attendances = None
        all_programs = None
        weekly_reports = None
        campuses = None
        lecturer_qs_for_current_user = None
    # Return the filtered data
    return {
        "program_offerings_for_current_user": program_offerings_for_current_user,
        "course_offerings_for_current_user": course_offerings_for_current_user,
        "programs_for_current_user": programs_for_current_user,
        "courses_for_current_user": courses_for_current_user,
        "students": students,
        "attendances": attendances,
        "all_programs": all_programs,
        "weekly_reports": weekly_reports,
        "campuses": campuses,
        "lecturer_qs_for_current_user": lecturer_qs_for_current_user,
    }


def get_online_offline_program(programs_for_current_user):
    if programs_for_current_user is not None:
        online_programs_for_current_user = programs_for_current_user.filter(
            Q(program_offerings__offering_mode="online")
        )
        offline_programs_for_current_user = programs_for_current_user.filter(
            ~Q(program_offerings__offering_mode="online")
        )
    else:
        online_programs_for_current_user = None
        offline_programs_for_current_user = None
    return {
        "online_programs_for_current_user": online_programs_for_current_user,
        "offline_programs_for_current_user": offline_programs_for_current_user,
    }


def get_online_offline_courses(courses_for_current_user):
    if courses_for_current_user is not None:
        online_courses_for_current_user = courses_for_current_user.filter(
            Q(temp_id__endswith="D")
        )
        blended_courses_for_current_user = courses_for_current_user.exclude(
            Q(temp_id__endswith="D")
        )
    else:
        online_courses_for_current_user = None
        blended_courses_for_current_user = None

    return {
        "online_courses_for_current_user": online_courses_for_current_user,
        "blended_courses_for_current_user": blended_courses_for_current_user,
    }


def get_online_offline_program_offerings(program_offerings_for_current_user):
    if program_offerings_for_current_user is not None:
        online_program_offerings_for_current_user = (
            program_offerings_for_current_user.filter(Q(offering_mode="online"))
        )
        blended_program_offerings_for_current_user = (
            program_offerings_for_current_user.exclude(Q(offering_mode="online"))
        )
    else:
        online_program_offerings_for_current_user = None
        blended_program_offerings_for_current_user = None

    return {
        "online_program_offerings_for_current_user": online_program_offerings_for_current_user,
        "blended_program_offerings_for_current_user": blended_program_offerings_for_current_user,
    }


def get_online_offline_course_offerings(course_offerings_for_current_user):
    if course_offerings_for_current_user is not None:
        online_course_offerings_for_current_user = (
            course_offerings_for_current_user.filter(Q(offering_mode="online"))
        )
        blended_course_offerings_for_current_user = (
            course_offerings_for_current_user.exclude(Q(offering_mode="online"))
        )
    else:
        online_course_offerings_for_current_user = None
        blended_program_offerings_for_current_user = None

    return {
        "online_course_offerings_for_current_user": online_course_offerings_for_current_user,
        "blended_course_offerings_for_current_user": blended_course_offerings_for_current_user,
    }


def default_start_and_end_date():
    current_date = datetime.now()

    # start date : 1st jan of last year and end date 31st dec of current year
    # default_start_date = datetime(current_date.year - 2, 1, 1).strftime('%Y-%m-%d')  # 1st Jan of lst year
    # default_end_date=datetime(current_date.year,12,31).strftime('%Y-%m-%d')

    # calculate current quarter start and end date
    start_date = current_date.replace(
        month=((current_date.month - 1) // 3) * 3 + 1, day=1
    )
    next_quarter_start_date = start_date.replace(month=start_date.month + 3, day=1)
    end_date = next_quarter_start_date - timedelta(days=1)

    default_start_date = start_date
    default_end_date = end_date

    print("default Start Date of Current Quarter:", start_date.strftime("%Y-%m-%d"))
    print("default End Date of Current Quarter:", end_date.strftime("%Y-%m-%d"))

    # default_end_date = datetime(2024, 3, 31).strftime('%Y-%m-%d')

    return default_start_date, default_end_date


def filter_data_based_on_date_range(
    start_date,
    end_date,
    programs_for_current_user,
    courses_for_current_user,
    program_offerings_for_current_user,
    course_offerings_for_current_user,
    attendances,
    weekly_reports,
    campuses,
    lecturer_qs_for_current_user,
):
    # print(" programs for current user value for date filter function  ",program_offerings_for_current_user)

    default_start_date, default_end_date = default_start_and_end_date()
    if not start_date:
        start_date = default_start_date
    if not end_date:
        end_date = default_end_date

    # filter data according to start and end date
    if start_date and end_date:
        print(f"Start date :{start_date} and end date :{end_date} by date filter form ")

        if course_offerings_for_current_user is not None:
            course_offerings_for_current_user = (
                course_offerings_for_current_user.filter(
                    Q(start_date__gte=start_date) & Q(start_date__lte=end_date)
                ).distinct()
            )

            print(
                f"course offerings for current user after date filter :{course_offerings_for_current_user}"
            )
            for co in course_offerings_for_current_user:
                print(f"{co.start_date} :{co.end_date}")
        else:
            print(
                f"no course offerings for current date filter: {start_date} to {end_date}"
            )

        if program_offerings_for_current_user is not None:
            # program_offerings_for_current_user=program_offerings_for_current_user.filter(
            #        Q(start_date__gte=start_date)| Q(end_date__lte=end_date))

            program_offerings_for_current_user = program_offerings_for_current_user.filter(
                student_enrollments__course_offering__in=course_offerings_for_current_user
            ).distinct()

            print(
                f"program offerings for current user after date filter :{program_offerings_for_current_user}"
            )
            for po in program_offerings_for_current_user:
                print(f"{po.program.name} :{po.start_date} :{po.end_date}")
                co_list = []
                for student_enrollment in po.student_enrollments.all():

                    co = student_enrollment.course_offering
                    if co not in co_list:
                        print(
                            f"  - Course: {co.course.name}, Start Date: {co.start_date}, End Date: {co.end_date}"
                        )
                    co_list.append(co)
        else:
            print(
                f"no program offerings for current date filter: {start_date} to {end_date}"
            )

        if courses_for_current_user is not None:
            # courses_for_current_user = courses_for_current_user.filter(
            #                                                 Q(course_offerings__start_date__gte=start_date)
            #                                                 | Q(course_offerings__end_date__lte=end_date)
            #                                             ).distinct()
            courses_for_current_user = courses_for_current_user.filter(
                course_offerings__in=course_offerings_for_current_user
            ).distinct()

        # all program and course need to be shown
        if programs_for_current_user is not None:
            # print(" date filter initializing for programs for current user ",programs_for_current_user)
            # for p in programs_for_current_user:
            #     for po in p.program_offerings.all():
            #         print(f"PO:{po} : start date :{po.start_date} and end date :{po.end_date}")

            # active_programs = programs_for_current_user.filter(
            #                                                 Q(program_offerings__start_date__gte=start_date)
            #                                                 | Q(program_offerings__end_date__lte=end_date)
            #                                             ).distinct()
            # # Get the inactive programs (programs that do not match the date criteria)
            # inactive_programs = programs_for_current_user.exclude(id__in=active_programs.values_list('id', flat=True)).distinct()

            active_programs = programs_for_current_user.filter(
                program_offerings__student_enrollments__course_offering__in=course_offerings_for_current_user
            ).distinct()
            # Get the inactive programs (programs that do not match the date criteria)
            inactive_programs = programs_for_current_user.exclude(
                id__in=active_programs.values_list("id", flat=True)
            ).distinct()

            programs_for_current_user = active_programs
            active_programs_for_current_user = active_programs

            inactive_programs_for_current_user = inactive_programs
            print(
                f" active  for current user after date filter {start_date} to {end_date} :{active_programs_for_current_user}"
            )
            print(
                f" inactive  for current user after date filter {start_date} to {end_date} :{inactive_programs_for_current_user}"
            )
            # print(len(programs_for_current_user))
            # print(len(inactive_programs_for_current_user))
        else:
            active_programs_for_current_user = None
            inactive_programs_for_current_user = None

        if attendances is not None:
            attendances = attendances.filter(
                Q(attendance_date__gte=start_date) & Q(attendance_date__lte=end_date)
            ).distinct()
            print(
                f" attendances for current date filter {start_date} to {end_date} , attendance count :{len(attendances)}"
            )

        if weekly_reports is not None:
            # weekly_reports=weekly_reports.filter(sessions__attendance_date__gte=start_date)
            weekly_reports = weekly_reports.filter(
                sessions__attendance_date__range=[start_date, end_date]
            )
        if campuses is not None:
            campuses = Campus.objects.prefetch_related(
                "users", "users__student_profile__student_enrollments__course_offering"
            )
            print(
                f" campuses before current date filter {start_date} to {end_date} :{campuses}"
            )
            # campuses=campuses.filter(users__student_profile__student_enrollments__course_offering__in=course_offerings_for_current_user).distinct()
            campuses = campuses.filter(
                users__student_profile__student_enrollments__course_offering__in=course_offerings_for_current_user
            ).distinct()

            # campuses=campuses
            print(
                f" campuses after current date filter {start_date} to {end_date} :{campuses}"
            )

        if lecturer_qs_for_current_user is not None:
            lecturer_qs_for_current_user = lecturer_qs_for_current_user.filter(
                staff_course_offering_relations__course_offering__in=course_offerings_for_current_user
            ).distinct()
            print(
                f" lecturer_qs_for_current_user for current date filter {start_date} to {end_date} :{lecturer_qs_for_current_user}"
            )

    return {
        "program_offerings_for_current_user": program_offerings_for_current_user,
        "course_offerings_for_current_user": course_offerings_for_current_user,
        "programs_for_current_user": programs_for_current_user,
        "courses_for_current_user": courses_for_current_user,
        "active_programs_for_current_user": active_programs_for_current_user,
        "inactive_programs_for_current_user": inactive_programs_for_current_user,
        "attendances": attendances,
        "weekly_reports": weekly_reports,
        "start_date": start_date,
        "end_date": end_date,
        "campuses": campuses,
        "lecturer_qs_for_current_user": lecturer_qs_for_current_user,
    }
