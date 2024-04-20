from django.db import models
from base.models import BaseModel,Campus
from customUser.models import Student, Staff
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Q


from utils.function.helperAttendance import get_attendance_percentage,get_attendance_percentage_by_program,get_attendance_percentage_by_course,get_attendance_percentage_by_program_offering,get_attendance_percentage_by_course_offering,get_attendance_percentage_by_attendances,get_engagement_percentage_by_course,get_engagement_percentage_by_program,get_engagement_percentage_by_course_offering,get_engagement_percentage_by_course_offering_for_student
from utils.function.helperGetAtRiskStudent import get_no_of_at_risk_students_by_course_offering,get_no_of_at_risk_students_by_program_offering,get_no_of_at_risk_students_by_course,get_no_of_at_risk_students_by_program
from utils.function.helperGetTotalNoOfStudents import get_total_no_of_student_by_program,get_total_no_of_student_by_course, get_all_student_enrollments_by_program, get_all_student_enrollments_by_program_offering, get_all_student_enrollments_by_course_offering
from utils.function.BaseValues_List import OFFERING_CHOICES
from utils.function.helperGetChartData import get_chart_data_attendance_report


class ProgramAndCourseType(models.Model):
    name=models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Program and Course Type'
        verbose_name_plural = 'Program and Course Type'
        
    def __str__(self):
        return self.name

class Program(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    
    def get_list_of_online_course_for_selected_program(self):
        # return self.course.filter(offering_mode_is_online=True)
        list_of_online_course_for_selected_program=self.courses.all().filter(temp_id__endswith = "D")
        return list_of_online_course_for_selected_program

    def get_list_of_blended_course_for_selected_program(self):
        list_of_offline_course_for_selected_program=self.courses.all().exclude(temp_id__endswith = "D")
        return list_of_offline_course_for_selected_program
   
    
    def get_list_of_online_program_offerings_for_selected_program(self):
        list_of_online_program_offerings_for_selected_program = self.program_offerings.filter(offering_mode="online")
        return list_of_online_program_offerings_for_selected_program

    def get_list_of_blended_program_offerings_for_selected_program(self):
        list_of_blended_program_offerings_for_selected_program = self.program_offerings.filter(
            Q(offering_mode="blended") | Q(offering_mode="micro cred")
        )
        return list_of_blended_program_offerings_for_selected_program

    def calculate_program_efts(self):
        total_credit=0
        for c in self.courses.all():
            if c.course_efts is not None :
              
                total_credit+=c.course_efts
        return round(total_credit, 6)
            

    # attendance percentage is only for blended/offline program, inactive and online program doesn't have attendance
    def calculate_attendance_percentage(self):
        # attendance Percentage is only for offline program 
        return get_attendance_percentage_by_program(program=self)
    
    def calculate_engagement_percentage_for_online_program(self,offering_mode='online'):
   
        return get_engagement_percentage_by_program(program=self, offering_mode=offering_mode)
    
    def calculate_engagement_percentage_for_blended_program(self,offering_mode='blended'):
    
        return get_engagement_percentage_by_program(program=self, offering_mode=offering_mode)
  
    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_program(program=self)
    
    def calculate_total_student_enrollments(self,offering_mode='all'):
        return get_all_student_enrollments_by_program(program=self,offering_mode=offering_mode)
        
    
    def calculate_total_student_enrollments_for_online_program(self,offering_mode='online'):
        return get_all_student_enrollments_by_program(program=self,offering_mode=offering_mode)
    
    def calculate_total_student_enrollments_for_offline_program(self,offering_mode='all'):
        return get_all_student_enrollments_by_program(program=self,offering_mode=offering_mode)
    
    # wrong method getting all value incorrect and repeated 
    def calculate_total_no_of_student(self,offering_mode='all'):
        return get_total_no_of_student_by_program(program=self,offering_mode=offering_mode)

    # wrong method getting all value incorrect and repeated 
    def calculate_total_no_of_student_for_online_program(self,offering_mode="online"):

        return get_total_no_of_student_by_program(program=self,offering_mode=offering_mode)
    # wrong method getting all value incorrect and repeated 
    def calculate_total_no_of_student_for_offline_program(self,offering_mode="offline"):

        return get_total_no_of_student_by_program(program=self,offering_mode=offering_mode)
   
    

    def __str__(self):
        return f'{self.temp_id}-{self.name}'

class Course(BaseModel):
    name=models.CharField(max_length=255,null=True,blank=True)
    description=models.CharField(max_length=255,null=True,blank=True)
    key_components=models.CharField(max_length=255,null=True,blank=True)
    program_link = models.URLField(max_length=255, null=True, blank=True)
    total_credit=models.PositiveIntegerField(null=True,blank=True)
    duration_in_week=models.PositiveIntegerField(null=True,blank=True)
    program = models.ManyToManyField(Program, blank=True, related_name='courses')
    course_efts=models.FloatField(null=True,blank=True)

    def get_offering_mode_is_online(self):
        if self.temp_id and self.temp_id[-1]=="D":
            return True
        else:
            return False

    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_course(course=self)
    
    def calculate_attendance_percentage(self):
        return get_attendance_percentage_by_course(course=self)
    
    def calculate_total_no_of_student_for_online_course(self,offering_mode="online"):
        return get_total_no_of_student_by_course(course=self,offering_mode=offering_mode)
    
    def calculate_total_no_of_student_for_offline_course(self,offering_mode="offline"):
        return get_total_no_of_student_by_course(course=self,offering_mode=offering_mode)
    
    def calculate_total_no_of_student(self,offering_mode='all'):
        return get_total_no_of_student_by_course(course=self,offering_mode=offering_mode)
    
    def calculate_engagement_percentage(self):
        
        return get_engagement_percentage_by_course(course=self)
    
    
    def __str__(self):
        return f'{self.temp_id}-{self.name}'




class CourseOffering(BaseModel):
    
    # OFFERING_CHOICES1 = [
    #     ('online', 'ONLINE'),
    #     ('micro cred', 'MICRO CRED'),
    #     ('blended', 'BLENDED'),
    # ]

    course=models.ForeignKey(Course, verbose_name=("course"), on_delete=models.CASCADE,null=True,blank=True,related_name='course_offerings')
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)

    # both field below has to go with student or linked with result table with each student with each course offering
    result_status_code=models.CharField(max_length=255,null=True,blank=True)
    result_status=models.CharField(max_length=255,null=True,blank=True)

    student = models.ManyToManyField(Student,blank=True ,related_name='course_offerings')
    teacher = models.ManyToManyField(Staff,blank=True ,related_name='course_offerings')
    offering_mode = models.CharField(max_length=10,choices=OFFERING_CHOICES,default='online',blank=True, null=True,help_text='Select the mode of course offering: Online, Offline, or Blended'
    )
    
    def get_week_numbers(self):
        start_date=self.start_date
        end_date=self.end_date
        
        num_weeks=(end_date-start_date).days//7
        week_numbers = [(str(week), str(week)) for week in range(1, num_weeks + 1)]
        
        return  week_numbers  # Add an empty choice and return
        
        
    def calculate_student_attendance_percentage(self):
        attendances=self.attendances.all()
        
        present=attendances.filter(is_present='present').count()
        informed_absent=attendances.filter(is_present='informed absent').count()
        absent=attendances.filter(Q(is_present='absent')|Q(is_present='tardy')).count()
        total_attendances=attendances.count()
        if total_attendances>0 and total_attendances == present+informed_absent+absent:
            present_percentage=f'{(present / total_attendances) * 100:.2f}%'
            informed_absent_percentage=f'{(informed_absent / total_attendances) * 100:.2f}%'
            absent_percentage=f'{(absent / total_attendances) * 100:.2f}%'
        else:
            present_percentage=0
            informed_absent_percentage=0
            absent_percentage=0
            
        return{
            'present_percentage':present_percentage ,
            'informed_absent_percentage':informed_absent_percentage ,
            'absent_percentage':absent_percentage ,
        }
    
    def calculate_student_attendance_chart_data(self):
        if self.attendances.all():
            chart_data_attendance_report_attendance,chart_data_attendance_report_engagement ,chart_data_attendance_report_action=get_chart_data_attendance_report(attendances=self.attendances.all())
        else:
            chart_data_attendance_report_attendance=None
        return chart_data_attendance_report_attendance
        
    
    def calculate_duration_in_week(self):
        start_date=self.start_date
        end_date=self.end_date
        days_difference =(end_date-start_date).days
        
        no_of_weeks=days_difference//7
        
        if days_difference%7!=0:
            no_of_weeks+=1
        
        
        starting_week_number=start_date.isocalendar()[1]
        ending_week_number=end_date.isocalendar()[1]
        # print(start_date,":",end_date)
        # print(starting_week_number,":",ending_week_number)
        
        return {"no_of_weeks":no_of_weeks,"starting_week_number":starting_week_number,"ending_week_number":ending_week_number}
        
        
    def calculate_attendance_percentage(self): 
        if self.offering_mode=='online':
            return "Not Applicable"
        else:
            # return get_attendance_percentage_by_course_offering(course_offering=self,total_sessions=0,present_sessions=0)
            return get_attendance_percentage_by_attendances(self.attendances.all())
    
    def calculate_engagement_percentage(self):
        
        return get_engagement_percentage_by_course_offering(course_offering=self)
    
    def calculate_attendance_percentage_for_student(self, student):
        if self.offering_mode == 'online':
            return "Not Applicable"
        else:
            student_attendance_records = self.attendances.filter(student=student)
            return get_attendance_percentage_by_attendances(student_attendance_records)
    
    def calculate_engagement_percentage_for_student(self,student):
        
        return get_engagement_percentage_by_course_offering_for_student(course_offering=self,student=student)  
       
     
   
    
    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_course_offering(course_offering=self)

    # dont use this method 
    def calculate_total_no_of_student(self):
        # Assuming you have a reverse relationship from Program to ProgramOffering named 'program_offerings'
        return self.student.count()
       
    def get_all_students(self):
        students = self.student.all()
        # print("Students from Program Offering:", students)
        return students
    
    
    
    def calculate_total_student_enrollments(self):
        
        return get_all_student_enrollments_by_course_offering(course_offering=self)
    
    def list_program_offering(self):
        student_enrollments=self.student_enrollments.all()
        program_offerings_list = set()  # Use a set to store unique course offerings
        for student_enrollment in student_enrollments:
            program_offering = student_enrollment.program_offering
            program_offerings_list.add(program_offering)  # Add each course offering to the set
        
        # Convert the set back to a list if necessary
        program_offerings_list = list(program_offerings_list)


        return program_offerings_list
    
    def __str__(self):
        return f'{self.temp_id}-{self.course.name}'

    
    
    
    
class ProgramOffering(BaseModel):
    program=models.ForeignKey(Program, verbose_name=("program"), on_delete=models.CASCADE,null=True,blank=True,related_name="program_offerings")
    start_date=models.DateField( auto_now=False, auto_now_add=False)
    end_date=models.DateField( auto_now=False, auto_now_add=False)
    remark=models.TextField(max_length=255,blank=True,null=True)
    program_leader=models.ManyToManyField(Staff,blank=True ,null=True,related_name='program_offerings')
    student=models.ManyToManyField(Student,blank=True,related_name='program_offering')
    offering_mode = models.CharField(max_length=10,choices=OFFERING_CHOICES,default='online',blank=True, null=True,help_text='Select the mode of course offering: Online, Offline, or Blended'
    )
    def calculate_attendance_percentage(self):
        return get_attendance_percentage_by_program_offering(program_offering=self,total_sessions=0,present_sessions=0)

    def calculate_no_at_risk_student_for_last_week(self):
        return get_no_of_at_risk_students_by_program_offering(program_offering=self)

    def calculate_total_student_enrollments(self):
        return get_all_student_enrollments_by_program_offering(program_offering=self)

        

    def list_course_offerings(self):
        
        student_enrollments=self.student_enrollments.all()
        course_offerings_list = set()  # Use a set to store unique course offerings
        for student_enrollment in student_enrollments:
            course_offering = student_enrollment.course_offering
            course_offerings_list.add(course_offering)  # Add each course offering to the set
        
        # Convert the set back to a list if necessary
        course_offerings_list = list(course_offerings_list)


        return course_offerings_list
    
    
    # this method is incorrect , it will calculate all student based on course Offering no on program offring 
    def calculate_total_no_of_student(self):
        total_students=set()
        student_enrollments=self.student_enrollments.all()
        for student_enrollment in student_enrollments:
            total_students.add(student_enrollment.student)

        return total_students
     
    
    # dont use ths method anymore
    def get_all_students(self):
        students = self.student.all()
        # print("Students from Program Offering:", students)
        return students

    def __str__(self):
        return f'{self.temp_id}-{self.program.name}'


   

class StaffCourseOfferingRelations(BaseModel):
    CAMPUS_CHOICES = [(campus.id, campus.name) for campus in Campus.objects.all()]
    CAMPUS_CHOICES.append(('all', 'All'))  # Append the 'all' choice
    
    staff=models.ForeignKey(Staff, verbose_name='staff', on_delete=models.PROTECT, related_name='staff_course_offering_relations')
    course_offering=models.ForeignKey(CourseOffering, verbose_name='course_offering', on_delete=models.PROTECT,related_name='staff_course_offering_relations')
    
    students_by_campus = models.CharField(verbose_name='campus', max_length=100, choices=CAMPUS_CHOICES, default='all')
    
    def __str__(self):
        return f"{self.course_offering}:{self.staff.staff} "

class StaffProgramOfferingRelations(BaseModel):
    CAMPUS_CHOICES = [(campus.id, campus.name) for campus in Campus.objects.all()]
    CAMPUS_CHOICES.append(('all', 'All'))  # Append the 'all' choice
    
    staff=models.ForeignKey(Staff, verbose_name='staff', on_delete=models.PROTECT, related_name='staff_program_offering_relations')
    program_offering=models.ForeignKey(ProgramOffering, verbose_name='program_offering', on_delete=models.PROTECT,related_name='staff_program_offering_relations')
    
    students_by_campus = models.CharField(verbose_name='campus', max_length=100, choices=CAMPUS_CHOICES, default='all')

class StaffProgramRelations(BaseModel):
    CAMPUS_CHOICES = [(campus.id, campus.name) for campus in Campus.objects.all()]
    CAMPUS_CHOICES.append(('all', 'All'))  # Append the 'all' choice
    
    staff=models.ForeignKey(Staff, verbose_name='staff', on_delete=models.PROTECT, related_name='staff_program_relations')
    program=models.ForeignKey(Program, verbose_name='program', on_delete=models.PROTECT,related_name='staff_program_relations')
    
    students_by_campus = models.CharField(verbose_name='campus', max_length=100, choices=CAMPUS_CHOICES, default='all')
    
    