from django.contrib import admin
from program.models import Program, Course,ProgramOffering, CourseOffering,StaffProgramOfferingRelations,StaffProgramRelations
from customUser.models import Student
from report.models import WeeklyReport
from customUser.admin import StaffCourseOfferingRelationInline, StaffProgramRelationInline

from report.models import Attendance

class CourseInline(admin.StackedInline):  # You can use TabularInline if you prefer a more compact display.
    model = Program.courses.through
    extra = 1  # Number of empty forms to display


class ProgramOfferingInline(admin.StackedInline):
    model=ProgramOffering
    extra=1
    
class ProgramAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','description','get_total_enrollment','get_total_students','get_total_online_enrollment','get_total_online_students','get_offline_enrollment','get_total_offline_students','calculate_total_no_of_student','calculate_attendance_percentage','calculate_no_at_risk_student_for_last_week']
    
    inlines = [StaffProgramRelationInline,ProgramOfferingInline,CourseInline]
    
    def calculate_attendance_percentage(self, obj):
        return obj.calculate_attendance_percentage()
    calculate_attendance_percentage.short_description = 'Attendance Percentage'

    def calculate_no_at_risk_student_for_last_week(self, obj):
        return len(obj.calculate_no_at_risk_student_for_last_week())
    calculate_no_at_risk_student_for_last_week.short_description = 'No. of At-Risk Students (Last Week)'

    # old method 
    def calculate_total_no_of_student(self,obj):
        return len( obj.calculate_total_no_of_student())
    calculate_total_no_of_student.short_description = 'No. of  Students'
    
    def get_total_enrollment(self,obj):
        return len(obj.calculate_total_student_enrollments(offering_mode='all'))
    get_total_enrollment.short_description="Total Enrollment" 
    
    def get_total_students(self,obj):
        return len(set(obj.calculate_total_student_enrollments(offering_mode='all')))
    get_total_students.short_description="Total Students" 
    
    def get_total_online_enrollment(self,obj):
        return len(obj.calculate_total_student_enrollments(offering_mode='online'))
    get_total_online_enrollment.short_description='Total online Enrollments'
    
    def get_total_online_students(self,obj):
        return len(set(obj.calculate_total_student_enrollments(offering_mode='online')))
    get_total_online_students.short_description='Total online Students'
    
    
    def get_offline_enrollment(self,obj):
        return len(obj.calculate_total_student_enrollments(offering_mode='offline'))
    get_offline_enrollment.short_description='Total offline Enrollments'
    
    def get_total_offline_students(self,obj):
        return len(set(obj.calculate_total_student_enrollments(offering_mode='offline')))
    get_total_offline_students.short_description='Total offline Students'
    

class CourseAdmin(admin.ModelAdmin):
    list_display=['temp_id','name','calculate_total_no_of_student','description','course_efts']
    
    def calculate_total_no_of_student(self,obj):
        return len(obj.calculate_total_no_of_student())
    
    calculate_total_no_of_student.short_description = 'No. of  Students'

class ProgramOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','offering_mode','start_date','end_date','get_total_enrollment','get_total_students','get_total_enrollment_through_course_offering','get_list_of_course_offering','program')
    list_filter=['program','staff_program_offering_relations__staff','student_enrollments__course_offering','student_enrollments__student']
    def get_total_enrollment(self,obj):
        return len(obj.calculate_total_student_enrollments())
    get_total_enrollment.short_description="Total Enrollment"
    
    def get_total_students(self,obj):
        return len(set(obj.calculate_total_student_enrollments()))
    get_total_students.short_description="Total Students"
    
    def get_list_of_course_offering(self,obj):
        return obj.list_course_offerings()
    get_list_of_course_offering.short_description="Course Offering's"
    
    # just to check enrollments , student count will always the same 
    def get_total_enrollment_through_course_offering(self,obj):
        course_offerings=obj.list_course_offerings()
        student_enrollments=[]
        student_set=set()
        for course_offering in course_offerings:
            student_enrollments_by_course_offering=course_offering.calculate_total_student_enrollments()
            
            # print(f" student_enrollments_by_course_offering :{student_enrollments_by_course_offering}")
            for student in student_enrollments_by_course_offering:
                all_enrollments=student.student_enrollments.all()
                for student_enrollment in all_enrollments:
            # Check if the student enrollment belongs to the program offering
                    if student_enrollment.program_offering == obj:
                        student_enrollments.append(student_enrollment)
                        student_set.add(student_enrollment.student)
            # student_enrollments.extend(students_enrollment_filtered_by_program_offering_only)
            # student_set.update(students_enrollment_filtered_by_program_offering_only)
        
        enrollment_count=len(student_enrollments)
        student_count=len(list(student_set))
        return f"{enrollment_count}/{student_count}"
    
    get_total_enrollment_through_course_offering.short_description="Total Student Enrollment/Count through Course Offering"
            



class AttendanceInline(admin.TabularInline):
    model= Attendance
    extra =1
    
class WeeklyReportInline(admin.TabularInline):
    model=WeeklyReport
    extra=0

class CourseOfferingAdmin(admin.ModelAdmin):
    list_display=('temp_id','course','offering_mode','start_date','end_date','get_total_enrollment','get_total_students','get_all_teacher','get_list_program_offering','result_status','result_status_code')
    list_filter=['course','staff_course_offering_relations__staff','student_enrollments__program_offering','student_enrollments__student']
    # inlines=[WeeklyReportInline,AttendanceInline]

    inlines=[StaffCourseOfferingRelationInline]
    
    def get_total_enrollment(self,obj):
        return len(obj.calculate_total_student_enrollments())
    get_total_enrollment.short_description="Total Enrollment"
    
    def get_total_students(self,obj):
        return len(set(obj.calculate_total_student_enrollments()))
    get_total_students.short_description="Total Students"
    
    
    def get_list_program_offering(self,obj):
        return obj.list_program_offering()
    get_list_program_offering.short_description="program Offering List"
    
    def get_all_teacher(self,obj):
        teachers = obj.staff_course_offering_relations.all()
        teacher_names = [f"{teacher.staff.staff.first_name} {teacher.staff.staff.last_name}" for teacher in teachers]
        return ", ".join(teacher_names) if teacher_names else "N/A"
    
    get_all_teacher.short_description="Teacher's"
class StaffProgramRelationsAdmin(admin.ModelAdmin):
    list_display=('staff','program')
    
    
admin.site.register(StaffProgramRelations,StaffProgramRelationsAdmin)
admin.site.register(Program, ProgramAdmin)

admin.site.register(Course,CourseAdmin)
admin.site.register(ProgramOffering,ProgramOfferingAdmin)
admin.site.register(CourseOffering,CourseOfferingAdmin)
