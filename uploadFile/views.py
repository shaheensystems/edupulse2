# views.py
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
import csv
from .forms import CSVModelForm,AttendanceUploadForm, CanvasStatsUploadForm,BulkAttendanceUploadForm
# from .forms import CSVUploadForm
# from .models import UploadFile
from .models import Csv,CanvasStatsUpload,BulkAttendanceUpload
from report.models import Attendance,WeeklyReport, StudentEnrollment
from customUser.models import Student
from program.models import Program,Course,ProgramOffering,CourseOffering
from customUser.models import NewUser,Student,Campus, Ethnicity, StudentFundSource
import csv
from django.contrib.auth.hashers import make_password
from datetime import datetime,timedelta
from django.urls import reverse

from report.views import get_week_number
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from utils.function.helperAttendance import get_create_or_update_attendance,get_create_or_update_weekly_report

from utils.function.helperExportFileFormat import export_excel_to_csv

from utils.function.BaseValues_List import ENGAGEMENT_CHOICE, ACTION_CHOICE, FOLLOW_UP_CHOICE
import pandas as pd



def create_groups_and_permission():
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    # Create groups if they don't exist
    head_of_school_group, _ = Group.objects.get_or_create(name='Head_of_School')
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    program_leader_group, _ = Group.objects.get_or_create(name='Program_Leader')
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    
    # Create or get the necessary content types
    content_type = ContentType.objects.get_for_models(
            Group, Permission
        )
     # Assign permissions to groups
    head_of_school_group.permissions.set(Permission.objects.all())
    admin_group.permissions.set(Permission.objects.all())
    program_leader_group.permissions.set(
            Permission.objects.exclude(
                content_type__in=content_type.values()
            ).exclude(
                codename__startswith='admin'
            )
        )
    teacher_permissions = Permission.objects.filter(
            codename__in=[
                'view_program', 'change_program',
                'view_programoffering', 'change_programoffering',
                'view_courseoffering', 'change_courseoffering',
                'view_course', 'change_course',
                'view_attendance'
            ]
        )
    teacher_group.permissions.set(teacher_permissions)
    
    

def handle_ethnicity(user, ethnicity_name):
    print("Ethnicity name ",ethnicity_name)
    if ethnicity_name:
        try:
            ethnicity = Ethnicity.objects.get(name=ethnicity_name)
        except Ethnicity.DoesNotExist:
            ethnicity = Ethnicity.objects.create(name=ethnicity_name)

        # Add the ethnicity to the user's ManyToManyField
        user.ethnicities.add(ethnicity)
        user.save()

def handle_student_fund_source(student,student_fund_source_code,student_fund_source_desc):
    
    if student_fund_source_code:
        fund_source, created = StudentFundSource.objects.get_or_create(
            name=student_fund_source_code,
            defaults={'description': student_fund_source_desc}
        )

        # Assign the fund_source to the student
        student.fund_source = fund_source
        if student_fund_source_code==2 or student_fund_source_code=='2':
            student.international_student=True
        student.save()

def handle_program_or_course_offering_mode(student_Program_offer_name):
    if not student_Program_offer_name:
        raise ValueError("student_Program_offer_name is not exits check student data file ")
    offering_mode = "blended"
    if student_Program_offer_name:
        # Check if the name contains "Micro-cred"
        if "Micro-cred" in student_Program_offer_name:
            offering_mode = "micro cred"
        # Check if the name contains "Distance"
        elif "Distance" in student_Program_offer_name:
            offering_mode = "online"
        # If neither condition is met, default to "Blended"
        else:
            offering_mode = "blended"

    return offering_mode
    

def handle_date_in_correct_format(date_str):
    print("raw data ",date_str)
    
    if date_str and '/' in date_str and len(date_str) > 7:
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            # Extract the date part and return it as a string in "YYYY-MM-DD" format
            formatted_date = date_obj.date()
            formatted_date_str = formatted_date.strftime("%Y-%m-%d")
            print("date converted successfully", formatted_date_str)
            return formatted_date_str
            
        except ValueError:
            # Handle invalid date format here, if needed
            print(f"Invalid date format: {date_str}")
            return None
            # return datetime.strptime('01/01/2001', "%d/%m/%Y")
    else:
        # Handle the case where date_str does not exist or is not in the expected format
        print("data invalid for date return None")
        return None

def update_or_create_campus(data):
    # Check if the program_code exits and doesn't contain spaces
    if data['student_campus_temp_id'] :
        try:
            campus = Campus.objects.get(temp_id=data['student_campus_temp_id'])
            # If found, update the program_desc
            campus.name = data['student_campus_temp_id']
            campus.save()
            print("Campus updated successfully")
        except Campus.DoesNotExist:
            # If not found, create a new program object
            Campus.objects.create(temp_id=data['student_campus_temp_id'], 
                                  name=data['student_campus_temp_id'])
            print("Campus created successfully")
    else:
        print(f"Ignoring campus with code '{data['student_campus_temp_id']}' due to data not valid ")


def updated_or_create_user(data):
    print("initializing  create or update user ")
    if data['student_id'] and data['student_id'].isdigit():
        update_or_create_campus(data)
        try:
            user=NewUser.objects.get(temp_id=data['student_id'])
            # user.username=data['student_id'], # updated username as string ('20220756',) need attention here 
            user.first_name=data['student_fname']
            user.last_name=data['student_lname']
            user.dob=handle_date_in_correct_format(data['student_dob'])
            user.email=data['student_email']

            # user.phone=data['student_mobile']
            
            student_mobile_raw = data.get('student_mobile', '')
            if student_mobile_raw.isdigit() and len(student_mobile_raw)<13:
                
                student_mobile = int(student_mobile_raw)
                print("Student Mobile Number :",student_mobile)
                # Assign the validated integer to user.phone
                user.phone = student_mobile
            else:
                # Handle the case where student_mobile is not a valid integer
                print(f"Invalid student_mobile value: {student_mobile_raw}")
                # You can choose to set a default value or handle it as appropriate
                user.phone = None  # or any other default value


            user.nationality=data['student_nationality']
            # update Ethnicities 
            handle_ethnicity(user,data['student_ethnicity1'])
            handle_ethnicity(user,data['student_ethnicity2'])
            handle_ethnicity(user,data['student_ethnicity3'])

            user.campus=Campus.objects.get(temp_id=data['student_campus_temp_id']) # link campus with User while creating new user 
            user.save()
            # print(user.first_name)
            # print(data['student_id'])
            # print(user.username)
            print(f"user:{user.username} updated successfully")

            
        except NewUser.DoesNotExist:
            student_mobile_raw = data.get('student_mobile', '')
            if student_mobile_raw.isdigit() and len(student_mobile_raw)<13:
                student_mobile = int(student_mobile_raw)
                print(student_mobile)
            
            else:
                # Handle the case where student_mobile is not a valid integer
                print(f"Invalid student_mobile value: {student_mobile_raw}")
                # You can choose to set a default value or handle it as appropriate
                student_mobile = None  # or any other default value

            new_user=NewUser.objects.create(
                temp_id=data['student_id'],
                username=data['student_id'],
                first_name=data['student_fname'],
                last_name=data['student_lname'],
                dob=handle_date_in_correct_format(data['student_dob']),
                email=data['student_email'],
                phone=student_mobile,
                nationality=data['student_nationality'],
                campus=Campus.objects.get(temp_id=data['student_campus_temp_id']), # link campus with User while creating new user 
                )
            # add ethnicity 
            handle_ethnicity(new_user,data['student_ethnicity1'])
            handle_ethnicity(new_user,data['student_ethnicity2'])
            handle_ethnicity(new_user,data['student_ethnicity3'])

             # Set the user's password
            password = f'WC{data["student_id"]}@{data["student_fname"]}'
            new_user.password = make_password(password)
            new_user.save()
            print(f'user"{new_user.username} cerated successfully')
    else:
        print(f"Ignoring program with code '{data['student_id']}' is not valid ")

def updated_or_create_student(data):
    print("Data for update or create students :",data)
    if data['student_id'] and data['student_id'].isdigit():
        # first cerate and updated user then create and updated student 
        updated_or_create_user(data)
        

        try:
            student=Student.objects.get(temp_id=data['student_id'])
            print(data['student_enrolment_status'])
            print('student object,',student.enrollment_status)
            # student.temp_id=data['student_id'], no changes while updated
            student.email_id=data['student_alternative_email']
            student.enrollment_status=data['student_enrolment_status']
            student.passport_number=data['student_passport_number']
            student.visa_number=data['student_visa_number']
            
            # student.visa_expiry_date=handle_date_in_correct_format(data['student_visa_expiry_date']),
            print('student object before save ,',student.enrollment_status)
            student.save()
            handle_student_fund_source(student,data['student_fund_source_code'],data['student_fund_source_desc'])
            print('student object after save ,',student.enrollment_status)
            # print(user.first_name)
            # print(data['student_id'])
            # print(user.username)
            print(f"student:{student.student.first_name}  updated successfully")

            
        except Student.DoesNotExist:
            new_student=Student.objects.create(
                temp_id=data['student_id'],
                email_id=data['student_alternative_email'],
                enrollment_status=data['student_enrolment_status'],
                passport_number=data['student_passport_number'],
                visa_number=data['student_visa_number'],
                # visa_expiry_date=handle_date_in_correct_format(data['student_visa_expiry_date']),
                student=NewUser.objects.get(temp_id=data['student_id']) # link user with student while creating new user not while update
                )
            new_student.save()
            handle_student_fund_source(new_student,data['student_fund_source_code'],data['student_fund_source_desc'])
            print(f'new student:{new_student.student.first_name} cerated successfully')
    else:
        print(f"Ignoring program with code '{data['student_id']}' is not valid ")


def update_or_create_program(data):
    # Check if the program_code exits and doesn't contain spaces
    if data['student_program_code'] and  ' ' not in data['student_program_code']:
        try:
            program = Program.objects.get(temp_id=data['student_program_code'])
            # If found, update the program_desc
            program.name = data['student_program_name']
            program.save()
            print("Program updated successfully")
        except Program.DoesNotExist:
            # If not found, create a new program object
            Program.objects.create(temp_id=data['student_program_code'], name=data['student_program_name'])
            print("Program created successfully")
    else:
        print(f"Ignoring program with code '{data['student_program_code']}' due to spaces in the code, not valid ")

# update_or_create_course(data['student_course_code'], data['student_course_name'],data['student_program_code'])
def update_or_create_course(data):
    # Check if the program_code exits and doesn't contain spaces
    if data['student_course_code'] and  ' ' not in data['student_course_code']:
        try:
            linked_program=Program.objects.get(temp_id=data['student_program_code'])
            course = Course.objects.get(temp_id=data['student_course_code'])
            # If found, update the program_desc
            course.name = data['student_course_name']
            try:
                linked_program = Program.objects.get(temp_id=data['student_program_code'])
                course.course_efts=float(data['student_course_efts'])
                course.program.add(linked_program)
            except Program.DoesNotExist:
                # Handle the case where the program doesn't exist
                print(f"Program with code '{data['student_course_code']}' not found")
            course.save()
            print("course updated successfully")
        except Course.DoesNotExist:
            # If not found, create a new program object
            Course.objects.create(temp_id=data['student_course_code'], 
                                  name=data['student_course_name'],
                                  course_efts=float(data['student_course_efts']),
                                  )
            print("Course created successfully")
    else:
        print(f"Ignoring Course with code '{data['student_course_code']}' due to spaces in the code, not valid ")

def update_or_create_course_offering(data):
    print("start course offering :",data['student_course_offer_code'])
    print("start course offering start date  :",data['student_course_offer_start_date'])
    print("start course offering end date :",data['student_course_offer_end_date'])
    # Check if the program_code exits and doesn't contain spaces
    # if data['student_course_offer_code'] and  ' ' not in data['student_course_offer_code']:
    if data['student_course_offer_code'] : # some data has space between code 
        # validation for course_offering_name with linked course name
        try:
            course_offering = CourseOffering.objects.get(temp_id=data['student_course_offer_code'])
            # If found, update the program_desc
            course_offering.start_date=handle_date_in_correct_format(data['student_course_offer_start_date'])
            course_offering.end_date=handle_date_in_correct_format(data['student_course_offer_end_date'])
            course_offering.offering_mode=handle_program_or_course_offering_mode(data['student_Program_offer_name'])
            course_offering.save()
            print("course offering updated successfully")
        except CourseOffering.DoesNotExist:
             # If not found, create a new course_offering object
            start_date = handle_date_in_correct_format(data['student_course_offer_start_date'])
            end_date = handle_date_in_correct_format(data['student_course_offer_end_date'])
            CourseOffering.objects.create(
                temp_id=data['student_course_offer_code'],
                start_date=start_date,
                end_date=end_date,
                offering_mode=handle_program_or_course_offering_mode(data['student_Program_offer_name']),
            )
            print("Course offering created successfully")
        # linked student and course with course_offering
        try:
            course_offering = CourseOffering.objects.get(temp_id=data['student_course_offer_code'])
            # linked_course=Course.objects.get(temp_id=data['student_course_code'])
            
            try:
                linked_student = Student.objects.get(temp_id=data['student_id'])
                course_offering.student.add(linked_student)
                course_offering.course=Course.objects.get(temp_id=data['student_course_code']) # one-to-one relationship
                course_offering.result_status_code=data['student_course_offer_result_code']
                course_offering.result_status=data['student_course_offer_result_status']
                course_offering.save()
            except Student.DoesNotExist:
                print("Student not exits cant linked with course offering ")

            
        except course_offering.DoesNotExist:
            # Handle the case where the program doesn't exist
            print(f"CourseOffering has error while creating or updating with code '{data['student_course_offering_code']}' n")        
            
    else:
        print(f"Ignoring Course offering with code '{data['student_course_offer_code']}' due to spaces in the code, not valid ")
def update_or_create_program_offering(data):
    print("start program offering :",data['student_program_offer_code'])
    # Check if the program_code exits and doesn't contain spaces
    # if data['student_program_offer_code'] and  ' ' not in data['student_program_offer_code']:
    if data['student_program_offer_code']:
        # validation for program_offering_name with linked course name
        try:
            program_offering = ProgramOffering.objects.get(temp_id=data['student_program_offer_code'])
            # If found, update the program_desc
            program_offering.start_date=handle_date_in_correct_format(data['student_program_offer_start_date'])
            program_offering.end_date=handle_date_in_correct_format(data['student_program_offer_end_date'])
            program_offering.offering_mode=handle_program_or_course_offering_mode(data['student_Program_offer_name'])
            program_offering.save()
            print("program offering updated successfully")
        except ProgramOffering.DoesNotExist:
            # If not found, create a new course_offering object
            ProgramOffering.objects.create(
                temp_id=data['student_program_offer_code'], 
                start_date=handle_date_in_correct_format(data['student_program_offer_start_date']),
                end_date=handle_date_in_correct_format(data['student_program_offer_end_date']),
                offering_mode=handle_program_or_course_offering_mode(data['student_Program_offer_name']),
                )
            print("program offering created successfully")
        # linked student and course with course_offering
        try:
            program_offering = ProgramOffering.objects.get(temp_id=data['student_program_offer_code'])
            # linked_course=Course.objects.get(temp_id=data['student_course_code'])
            linked_student = Student.objects.get(temp_id=data['student_id'])
            program_offering.student.add(linked_student)
            program_offering.program=Program.objects.get(temp_id=data['student_program_code']) # one-to-one relationship
            program_offering.save()
        except program_offering.DoesNotExist:
            # Handle the case where the program doesn't exist
            print(f"ProgramOffering has error while creating or updating with code '{data['student_program_offering_code']}' n")        
            
    else:
        print(f"Ignoring program offering with code '{data['student_program_offer_code']}' due to spaces in the code, not valid ")

def update_or_create_student_enrollment(data):
    print("Start student enrollment process for:", data['student_program_offer_code'])

    try:
        linked_student = Student.objects.get(temp_id=data['student_id'])
        linked_course_offering = CourseOffering.objects.get(temp_id=data['student_course_offer_code'])
        linked_program_offering = ProgramOffering.objects.get(temp_id=data['student_program_offer_code'])
    except ObjectDoesNotExist as e:
        print("Error for Student Enrollment process:", e)
        return

    if linked_student and linked_course_offering and linked_program_offering:
        # Proceed with the enrollment process
        try:
            # if data['student_id']=='20220228':
            #     print(linked_course_offering)
            #     print(linked_program_offering)
            student_enrollment_object, created = StudentEnrollment.objects.get_or_create(
                student=linked_student,
                course_offering=linked_course_offering,
                program_offering=linked_program_offering
            )

            if not created:
                # Update additional fields if needed
                student_enrollment_object.save()
            print("Student Enrollment created or update successfully :",student_enrollment_object)

        except IntegrityError as e:
            print("Error creating or updating StudentEnrollment:", e)
    
    
    
# Uplaod Student Data 
def Upload_file_view(request):
    form = CSVModelForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        form = CSVModelForm()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)

            header = next(reader, None)

            # Define a dictionary to map header names to variable names
            header_mappings = {
                                "offerid":"student_offer_id",
                                "clientofferregid":"student_offer_reg_id",
                                "client first name":"student_fname",
                                "client last name":"student_lname",
                                "client dob":"student_dob",
                                "client refinternal":"student_ref_internal",
                                "client refexternal":"student_id",
                                "client email":"student_email",
                                "client alternative email":"student_alternative_email",
                                "client mobile":"student_mobile",
                                "enrolment status":"student_enrolment_status",
                                "client post add1":"student_address_field1",
                                "client post add2":"student_address_field2",
                                "client post suburb":"student_address_suburb",
                                "client post pc":"student_address_postal_code",
                                "client post state":"student_address_estate",
                                "nz ethnicity 1":"student_ethnicity1",
                                "nz ethnicity 2":"student_ethnicity2",
                                "nz ethnicity 3":"student_ethnicity3",
                                "client passport number":"student_passport_number",
                                "client country of nationality":"student_nationality",
                                "visa number":"student_visa_number",
                                "visa expiry date":"student_visa_expiry_date",
                                "course code":"student_program_code",
                                "course desc":"student_program_name",
                                "course offer code":"student_program_offer_code",
                                "course offer desc":"student_Program_offer_name",
                                "cor start date":"student_program_offer_start_date",
                                "cor end date":"student_program_offer_end_date",
                                "unit code":"student_course_code",
                                "unit desc":"student_course_name",
                                "unit offer code":"student_course_offer_code",
                                "unit offer description":"student_course_offer_name",
                                "cuor start date":"student_course_offer_start_date",
                                "cuor end date":"student_course_offer_end_date",
                                "unit offer location":"student_campus_temp_id",
                                "unit efts factor":"student_course_efts",
                                "outcome code":"student_course_offer_result_code",
                                "outcome desc":"student_course_offer_result_status",
                                # new field
                                "client passport number":"student_passport_number",
                                "cuor fund source code":"student_fund_source_code",
                                "cuor fund source description":"student_fund_source_desc",
                                
            }

            # Create variables for each column
            data = {variable_name: None for header_name, variable_name in header_mappings.items()}

            for row in reader:
                if header is not None:
                    for header_name, variable_name in header_mappings.items():
                        index = header.index(header_name) if header_name in header else -1
                        if index >= 0:
                            data[variable_name] = row[index]

                # # Access the data using the variable names
                # # student_offer_id = data['student_offer_id']

                # # create object as needed for data by importing models here 
                
                # # add Program temp- student_program_code, student_program_desc
                # update_or_create_program(data=data)
               
                # # Print or process the variables
                # # print(data['student_program_code'])
                
                # # add Course temp- student_program_code, student_program_desc
                # update_or_create_course(data=data)

                # # add or update Student
                # updated_or_create_student(data)

                # # add course and program offering after creating student 
                # update_or_create_course_offering(data)
                # update_or_create_program_offering(data)
                update_or_create_student_enrollment(data)
                
                # create group and add permission 
                create_groups_and_permission()
                
                print("All data updated successfully !!!")

        obj.activated = True
        obj.save()
        # url = reverse('upload_file:upload_file')
    
   
    context = {
        'form': form,
        # 'current_user':request.user,
        }
   
    return render(request, 'upload/upload_file.html', context)



def Attendance_Upload_View(request, pk):
    course_offering = get_object_or_404(CourseOffering, id=pk)
    form = AttendanceUploadForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        obj = form.save(commit=False)
        # print(f'File name before opening: {obj.file_name.name}')
        form.save()
        form = AttendanceUploadForm()
    
         # Directly open and read the text file
        file_path = obj.file_name.path
        # print(file_path)
        # print("print object : ",obj)
        # print("print object status : ",obj.activated)
        # print("print object file name  : ",obj.file_name)
        try:
            with open(file_path, 'r',encoding='utf-16') as f:
                # Adjust the parsing logic based on the text file format
                lines = f.readlines()

                # Assuming the first section contains metadata and the second section contains data
                metadata_section = lines[:6]
                data_section = lines[7:]

                # Parse metadata
                metadata_dict = {line.split('\t')[0]: line.split('\t')[1].strip() for line in metadata_section}

                # Define a dictionary to map header names to variable names
                header_mappings = {
                    "Full Name": "full_name",
                    "Join Time": "join_time",
                    "Leave Time": "leave_time",
                    "Duration": "duration",
                    "Email": "student_email",
                    "Role": "role",
                    "Participant ID (UPN)": "participant_id",
                }

                # Parse data
                header_row = data_section[0] # first row header mapping 
                # print("header row :",header_row)
                header_columns = header_row.strip().split('\t')
                header_index_mapping = {header: header_columns.index(header) for header in header_mappings.keys()}

                # print("header Index mapping:",header_index_mapping)

                # Parse data
                for row in data_section[1:]: # Skip the header row
                    data = {variable_name: None for header_name, variable_name in header_mappings.items()}
                    columns = row.strip().split('\t')
                    # print("row wise data :",row)
                    # print("row wise column :",columns)
                    # print("data :",data)

                    for header_name, variable_name in header_mappings.items():
                        
                        if header_name in header_mappings:
                            index = header_index_mapping[header_name]
                           
                            # Check if index is an integer before using it
                            if isinstance(index, int) and 0 <= index < len(columns):
                                data[variable_name] = columns[index]
                            else:
                                print(f"Error: Index is not a valid integer - {index}")

                    
                    # course_offering=course_offering
                    student_email_id= data.get('student_email')
                    joining_time_str=data.get('join_time').strip('"\'')
                    # joining_time_str = joining_time_str.strip('"\'')
                    duration_str=data.get('duration')

                    # Convert data into proper format for attendance
                    
                    try:
                        joining_time_str = joining_time_str.strip()  # Strip leading/trailing whitespaces
                        attendance_date = datetime.strptime(joining_time_str, '%m/%d/%Y, %I:%M:%S %p')
                        
                    except ValueError:
                        print(f"Error: Unable to parse date string - {joining_time_str}")
                    
                    # Convert duration to total minutes
                    duration_parts = duration_str.split(' ')
                    total_minutes = 0

                    for part in duration_parts:
                        if 'h' in part:
                            total_minutes += int(part[:-1]) * 60
                        elif 'm' in part:
                            total_minutes += int(part[:-1])
                    if total_minutes>15:
                        is_present="present"
                    else:
                        is_present="absent"
                    student_id=student_email_id.split('@')[0] 
                   
                    #cant create student from this data
                    # student_obj, created = Student.objects.get_or_create(temp_id=student_id)
                   
                    try:
                        # if student exits 
                        student_obj = get_object_or_404(Student, temp_id=student_id)
                        print(f"Attendance detail : {course_offering}-{student_obj} on {attendance_date} is {is_present}")

                        # if student enrolled for course offering then create attendance
                        # print( "all courses enrolled by student :",student_obj.course_offerings.all)
                        if student_obj.course_offerings.filter(pk=course_offering.pk).exists():

                            newAttendance, created = Attendance.objects.get_or_create(
                            course_offering=course_offering,
                            student=student_obj,
                            attendance_date=attendance_date,
                            is_present= is_present,
                            )
                            newAttendance.save()
                            print("new attendance data :",newAttendance.is_present)
                            # generate weekly report for each student while marking attendance  with the attendance 
                            week_number=get_week_number(course_offering.start_date,attendance_date)
                            print("week number :",week_number)
                            if week_number>0:
                                weekly_report, created = WeeklyReport.objects.get_or_create(
                                    student=student_obj, course_offering=course_offering, week_number=week_number)

                                # weekly_report.sessions.add(newAttendance)
                                if not weekly_report.sessions.filter(Q(id=newAttendance.id) ).exists():
                                    # The newAttendance does not exist, so add it
                                    weekly_report.sessions.add(newAttendance)
                                else:
                                    # The newAttendance already exists
                                    print("Attendance already exists")
                                weekly_report.save()
                            else:
                                print("Error !!! attendance date is not belong to this course offering ")
                        else:
                            print("Student is not enrolled in current course offering while is mandatory for attendance upload  ")
                            print("Adding student in course offering ")
                            course_offering.student.add(student_obj)
                            if student_obj.course_offerings.filter(pk=course_offering.pk).exists() :
                               print("Student added to current course offering ")
                            else:
                                print("this statement means error in code while adding student to current course offering ")
                            
                    except student_obj.DoesNotExist:
                        print("Student doesn't exits , attendance cant be marked ")  


            obj.activated = True
            obj.save()  
            # print(data)
        except Exception as e:
             print(f'Error opening file: {e}')

    # pass      

    return render(request, 'upload/upload_attendance.html', {'form': form, "course_offering": course_offering})

def Canvas_weekly_report_upload_view(request, pk,week_number):
    form=CanvasStatsUploadForm(request.POST or None, request.FILES or None)
    course_offering = get_object_or_404(CourseOffering, id=pk)
    week_number=week_number
    weekly_reports = WeeklyReport.objects.filter(week_number=week_number, course_offering=course_offering)
    students = course_offering.student.filter(weekly_reports__week_number=week_number).distinct()
    # print("weekly report for all week:",weekly_reports)

    if form.is_valid():
        form.save()
        form = CanvasStatsUploadForm()
        obj = CanvasStatsUpload.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            header = next(reader, None)

            # Define a dictionary to map header names to variable names
            header_mappings = {
                                "Last page view time":"last_login_date",
                                "Page Views":"no_of_page_views",
                                "Email":"student_email_id",
                               
            }

            # Create variables for each column
            data = {variable_name: None for header_name, variable_name in header_mappings.items()}

            for row in reader:
                if header is not None:
                    for header_name, variable_name in header_mappings.items():
                        index = header.index(header_name) if header_name in header else -1
                        if index >= 0:
                            data[variable_name] = row[index]
                
                last_login_date=data['last_login_date']
                if len(last_login_date)>4:
                    last_login_status=True
                else:
                    last_login_status=False

                no_of_canvas_page_views=data['no_of_page_views']
                if no_of_canvas_page_views=="-":
                    no_of_canvas_page_views=0
                student_email_id=data['student_email_id']
                student_id=student_email_id.split('@')[0] 
                # print(f"Student id :{student_id} last login status is {last_login_status} on date {last_login_date} and total pages view in canvas is {no_of_canvas_page_views} ")

                for weekly_report in weekly_reports:
                    # print("student Id in weekly report",weekly_report.student.temp_id)
                    if student_id==weekly_report.student.temp_id:
                        print("Student Id matched : ",student_id)

                student_weekly_report = weekly_reports.filter(student__temp_id=student_id)

                if student_weekly_report:
                    print(f"Student weekly report exists for {student_id}")
                    # Update the specific WeeklyReport instance with the new data
                    student_weekly_report = student_weekly_report  # Ensure it's a single instance
                    student_weekly_report.no_of_pages_viewed_on_canvas = no_of_canvas_page_views
                    student_weekly_report.login_in_on_canvas = last_login_status
                    # student_weekly_report.save()
                else:
                    print("Student weekly report not exits ")
                # print("student weekly report ",student_weekly_report.login_in_on_canvas)
                # print("student weekly report ",student_weekly_report.no_of_pages_viewed_on_canvas)
                
        
        
        
        
        obj.activated = True
        obj.save()


    return render(request, 'upload/upload_canvas_weekly_report.html', {
        'form':form,
        'weekly_reports': weekly_reports,
        'students': students,
        'week_number':week_number,
        'course_offering':course_offering
        })

def Upload_bulk_attendance_view(request):
    bulk_attendance_form=BulkAttendanceUploadForm(request.POST or None,request.FILES or None)
   

    if request.method == 'POST':
        if bulk_attendance_form.is_valid():
            bulk_attendance_obj = bulk_attendance_form.save(commit=False)  # Save the form data but don't commit yet
            bulk_attendance_file = bulk_attendance_form.cleaned_data['file_name']
            timetable_file = bulk_attendance_form.cleaned_data['time_table']
            
            # Save bulk attendance file
            if bulk_attendance_file and timetable_file:
                bulk_attendance_obj.file_name = bulk_attendance_file
                # Save timetable file
                bulk_attendance_obj.time_table = timetable_file
            
            bulk_attendance_obj.save()  # Now commit the changes
            
            
            
            
            obj = BulkAttendanceUpload.objects.get(activated=False)
            
            bulk_attendance_file = bulk_attendance_form.cleaned_data['file_name']
            timetable_file = bulk_attendance_form.cleaned_data['time_table']
            
            print("attendance data file name :",bulk_attendance_file)
            print("timetable data file name :",timetable_file)
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday","Sunday"]
        
            # get the timetable details
            try:
                # with open(obj.time_table.path, 'r') as f:
                with open(obj.time_table.path, 'r', encoding='utf-8-sig') as f:  # Use 'utf-8-sig' encoding to handle BOM
        
                    time_table_data = []
                    reader = csv.reader(f)

                    header = next(reader, None)
                    
                    # print("time table header ",header)
                    # Define a dictionary to map header names to variable names
                    header_mappings = {
                                        "unit offer code":"course_offering_code",
                                        "unit offer description":"course_offering_name",
                                        "Lecturer":"lecturer_name",
                                        "Session Day":"session_day",
                                    
                    }

                    # Create variables for each column
                    data = {variable_name: None for header_name, variable_name in header_mappings.items()}

                    
                    
                    for row in reader:
                        # print("header value",header)
                        # print("row value :",row)
                        if header is not None:
                            for header_name, variable_name in header_mappings.items():
                                index = header.index(header_name) if header_name in header else -1
                                if index >= 0:
                                    data[variable_name] = row[index]
                    
                        # print("all time table data:",data)
                        course_offering_code = data['course_offering_code']
                        course_offering_name = data['course_offering_name']
                        lecturer_name = data['lecturer_name']
                        session_day = data['session_day']
                        
                        if session_day:
                            # print("row wise data :",course_offering_code,course_offering_name,lecturer_name,session_day)
                            # Find existing entry for course_offering_code in time_table_data
                            existing_entry = next((item for item in time_table_data if item["course_offering_code"] == course_offering_code), None)
                            if existing_entry:
                                # Update session list for existing entry
                                session_index=existing_entry['session_index']
                                session_index += 1
                                existing_entry["sessions"][f"session_{session_index}"]=session_day
                                existing_entry['session_index']= session_index
                                session_days = []
                                for i in range(1, existing_entry['session_index']):
                                    session_days.append(existing_entry['sessions'][f"session_{i}"])
                                session_days.append(session_day)  # Add the new session day
                                # print("before sort :",session_days)
                             
                                session_days=sorted(session_days,key=lambda x:days_of_week.index(x))
                                # print("after sort :",session_days)
                                # Update the session days in the existing entry
                                for i, day in enumerate(session_days, start=1):
                                    existing_entry['sessions'][f"session_{i}"] = day
                            else:
                                # Create a new entry for course_offering_code
                                session_index = 1
                                new_entry = {
                                    "course_offering_code": course_offering_code,
                                    "course_offering_name": course_offering_name,
                                    "lecturer_name":lecturer_name,
                                    "sessions": {f"session_{session_index}": session_day},
                                    'session_index':session_index
                                }
                                time_table_data.append(new_entry)

                    # print("time_table_data:",time_table_data)
                    # check time table data:
                    for time_table in time_table_data:
                        from program.models import StaffCourseOfferingRelations
                        from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

                        from customUser.models import Staff
                        # add staff to course offering 
                        course_offering_code=time_table['course_offering_code']
                        lecturer_name_list=time_table['lecturer_name'].split(",")
                        for lecturer_name in lecturer_name_list:
                            lecturer_name=lecturer_name.strip()
                        
                            try:
                                # Query for CourseOffering
                                course_offering_obj = CourseOffering.objects.get(temp_id=course_offering_code)
                            except ObjectDoesNotExist:
                                print(f"Course Offering from time table is not exist f or id : {course_offering_code}: {time_table['course_offering_name']}")
                                # Handle the case where CourseOffering with the specified temp_id does not exist
                                # Handle this exception according to your application logic
                            except MultipleObjectsReturned:
                                # Handle the case where multiple CourseOffering objects have the same temp_id
                                # Handle this exception according to your application logic
                                print(f"Multiple Course Offering exists for course id : {course_offering_code}: {time_table['course_offering_name']}")
                                
                            
                            try:
                                # Query for Staff
                                lecturer_name_lower = lecturer_name.lower()
                                
                                lecturer_obj = Staff.objects.get(Q(staff__first_name__iexact=lecturer_name_lower) | Q(staff__last_name__iexact=lecturer_name_lower))
                                
                            except ObjectDoesNotExist:
                                # Handle the case where Staff with the specified name does not exist
                                # Handle this exception according to your application logic
                                print(lecturer_name)
                                new_user, created = NewUser.objects.get_or_create(
                                    username=lecturer_name.lower(),
                                    defaults={
                                        'first_name': lecturer_name.upper(),
                                        # Add other fields and their default values here if needed
                                    }
                                )
                            

                                # Set the user's password
                                password = f'Admin@123'
                                new_user.password = make_password(password)
                                new_user.save()
                                new_lecturer=Staff.objects.create(
                                    staff=new_user,
                                    designation='Lecturer'
                                )
                                new_lecturer.save()
                                
                                if course_offering_obj:
                                    new_staff_course_offering_relationship_obj,created =StaffCourseOfferingRelations.objects.get_or_create(
                                        course_offering=course_offering_obj,
                                        staff=new_lecturer
                                    )
                                    new_staff_course_offering_relationship_obj.save()
                                    
                                
                            except MultipleObjectsReturned:
                                # Handle the case where multiple Staff objects have the same first or last name
                                # Handle this exception according to your application logic
                                print(f"Multiple teacher exists for course id : {course_offering_code}: {time_table['course_offering_name']}")
                                
                            
                            
                        # if time_table['sessions']:
                        #     sessions_obj = set()
                        #     for session in time_table['sessions'].values():  # Accessing values of the 'sessions' dictionary
                        #         sessions_obj.add(session)
                            
                        #     if len(time_table['sessions']) != len(sessions_obj):
                        #         print(f"Error: Session days are not unique for course offering {time_table['course_offering_code']}")
                        #     else:
                        #         print(f"Session days are unique for course offering {time_table['course_offering_code']}")
                        # else:
                        #     print(f"Error: No sessions available for course offering {time_table['course_offering_code']}")
                    
            except Exception as e:
               print(f'Error opening time table file: {e}')
            
            
            csv_file_path =export_excel_to_csv(obj.file_name.path)
            
            print(csv_file_path)
            
            
            
            # # upload attendance 
            # try:
            #     # df = pd.read_excel(obj.file_name.path)
    
            #     # # Print the DataFrame to see the data
            #     # print(df)

            #     with open(csv_file_path, 'r',encoding='utf-8') as f:
            #         # Adjust the parsing logic based on the text file format
            #         lines = f.readlines()

            #         # Assuming the first section contains metadata and the second section contains data
            #         header_section = lines[:2]
            #         data_section = lines[1:]
                    
            #         # print(header_section)
            #         # print("first row data :",data_section[1])
            #         header_line=data_section[0]
            #         # Split the header line by commas
            #         headers = header_line.split(';')
            #         # print("headers",headers)

            #         # Create a list to store the generated column headers
            #         column_headers = []

            #         # Track the session count for each week
            #         session_counts = {}

            #         for header in headers:
                        
                       
            #             if header == "Session 1" or header == "Session 2" or header == "Engagement" or header == "Action" or header == "Follow Up"  :
            #                 week = header  # Extract the week number from the header
                            
            #                 if week not in session_counts:
            #                     session_counts[week] = 0  # Initialize the session count for the week if it's not already present
            #                 session_counts[week] += 1  # Increment the session count for the week
            #                 # Generate the column header with the session count
            #                 # print("Header :",header)
            #                 # print("Week :",week)
            #                 # print("Session count :",session_counts)
            #                 column_headers.append(f"W{session_counts[week]} {header}")
            #             else:
            #                 column_headers.append(header)

            #         # Print the generated column headers
            #         # print("new column header",column_headers)            
            #         i=0
        
            #         # Create variables for each column
            #         data = {variable_name: None for variable_name in column_headers}
            #         # print("all data:",data)  
            #         # Process data rows
            #         for row in data_section[1:]:  # Skip the header row
            #             print("initial row wise data for attendance :",row)
                        
            #             row_data = row.split(';')
            #             # print("new column header",column_headers) 
            #             print("initial row wise data for attendance after split by ;:",row_data)
                        
            #             for header, value in zip(column_headers, row_data):
            #                 header_index = column_headers.index(header)
            #                 # print("header :",header)
            #                 # print("value :",value)
            #                 data[column_headers[header_index]] = value

            #             # Print the data for debugging
                    
                    
            #             # print("Data W1S1:", data['W1 Session 1'])
            #             # print("Data W1S2:", data['W1 Session 2'])
            #             # print("Data W2S1:", data['W2 Session 1'])
            #             # print("Data W2S2:", data['W2 Session 2'])
            #             print("row data:",data)
                        
            #             # process recording attendance start from here 
            #             student_id=data['Student ID']
            #             course_offering_id=data['Unit Offer Code']
            #             try:
            #                 course_offering_obj=CourseOffering.objects.get(temp_id=course_offering_id)
            #             except CourseOffering.DoesNotExist:
            #                 print(f"error !!! Course offering doesn't exits :{course_offering_id}")
                            
                            
                        
            #             try:
            #                 # student_obj = get_object_or_404(Student, temp_id=student_id)
            #                 student_obj = Student.objects.get(temp_id=student_id)
                            
            #             except Student.DoesNotExist:
            #                 print(f"error !!! Student doesn't exits :{student_id}")
                            
                            
                            
            #             if course_offering_obj and student_obj:
            #                 course_offering_start_date=course_offering_obj.start_date
                            
            #                 # Assuming course_offering_start_date is a datetime object
            #                 # course_offering_start_date = datetime.strptime(course_offering.start_date, "%Y-%m-%d")  # Convert to datetime object if it's a string
            #                 # course_offering_start_date_str = course_offering_start_date.strftime("%Y-%m-%d")

            #                 # Course Offering Starting Week 
            #                 course_starting_week_number = course_offering_start_date.isocalendar()[1]
            #                 year = course_offering_start_date.year

            #                 # print("Week number of the year for the course offering start date:", course_starting_week_number)
                                        
                                        
            #                 # print("CO start Date :",course_offering_obj.start_date)
            #                 # print(student_id,course_offering_id)
                            
            #                 # print("all data:",data) 
            #                 for key, value in data.items():
            #                     week_number=0
            #                     session_number=0
                                
            #                     # if key.endswith("Session 1"):
            #                     if "Session" in key:
            #                         print("initial row wise data for attendance :",row)
            #                         print("row data:",data)
            #                         print("key :",key ,"and Value :",value)
                                    
            #                         # day will be calculated by Course Offering and session
            #                         # with week and session and start date we wil find the session date 
            #                         if value and value != "NA":
            #                             week_number=key.split(" ")[0][1:]
            #                             session_number=key.split(" ")[2]
            #                             # print("week Number :",week_number)
            #                             # print("session Number :",session_number)
            #                             # print(key,":",value)
                                        
            #                             # value in import sheet has to be changed 
            #                             if value == "Informed - Absent" :
            #                                 is_present_value='Informed Absent'
            #                             else:
            #                                 is_present_value=value
                                        
                                        
            #                             if is_present_value.lower() not in ['absent', 'present','tardy','informed absent']:
            #                                 print("initial row wise data for attendance :",row)
            #                                 print("row data:",data)
            #                                 print("key :",key ,"and Value :",value)

            #                             # print("is Present:",is_present_value)
                                        
                                        
            #                             for data in time_table_data:
            #                                 if data['course_offering_code'] == course_offering_obj.temp_id:
            #                                     print("related time table  data to course offering ",data)
            #                                     session_day=data["sessions"][f"session_{session_number}"]
            #                                     session_day_number=days_of_week.index(session_day) + 1
                                            
            #                                     print("session day ",session_day ,":",session_day_number)
                                                
            #                             # print(course_offering_obj)
            #                             # Assuming week_number is already extracted from the key
            #                             if week_number.isdigit():
            #                                 week_number = int(week_number)
                                            
            #                                 # session week number is actual week number start from 1st jan to find out the exact date for attendance 
            #                                 session_week_number=course_starting_week_number + week_number-1
            #                                 # print("session week Number :",session_week_number)
            #                                 # Determine the year and ISO week day number of the Tuesday in the given week number
                                        
                                            
            #                                 iso_week_day_number = session_day_number  # Tuesday is the second day of the ISO week
            #                                 # Calculate the date of the Tuesday
            #                                 attendance_date = datetime.strptime(f"{year}-W{session_week_number}-{iso_week_day_number}", "%Y-W%W-%w").date()

            #                                 print(f"Date of {session_day} in week, {session_week_number}, {attendance_date}")
                                            
            #                                 # now record attendance in attendance model 
                                            
                                                
            #                                 get_create_or_update_attendance(student_obj=student_obj,
            #                                                                 course_offering_obj=course_offering_obj,
            #                                                                 attendance_date=attendance_date,
            #                                                                 is_present_value=is_present_value,
            #                                                                 week_number=week_number,
            #                                                                 session_number=session_number
            #                                                                 )
                                            
                                            
            #                             else:
            #                                 print("Invalid week number:", week_number)
                                            
            #                     if "Engagement" in key:
            #                         print("key :",key)
                                    
                                    
            #                         if value :
            #                             week_number=key.split(" ")[0][1:]
            #                             print("week Number :",week_number)
            #                             print("Engagement :",key,":",value)
            #                             if week_number.isdigit():
            #                                 week_number = int(week_number)
            #                                 if value =="NA":
            #                                     value="N/A"
            #                                 engagement_status=""
            #                                 for choice in ENGAGEMENT_CHOICE:
            #                                     if value == choice[1]:
            #                                         engagement_status=choice[0]
                                            
            #                                 if engagement_status == "":
            #                                     print(f"Error !!! Engagement Status value :{value} , doesn't not exits in Engagement Choice ")
            #                                 else :
                                                
            #                                         get_create_or_update_weekly_report(student_obj=student_obj,
            #                                                                     course_offering_obj=course_offering_obj,
            #                                                                     week_number=week_number,
            #                                                                     engagement_status=engagement_status,
            #                                                                     action_status= None,
            #                                                                     follow_up_status=None
            #                                                                     )
                                        
            #                             else:
            #                                 print("Invalid week number for Engagement Status update :", week_number) 
                                            
            #                     if "Action" in key:
            #                         print("key :",key)
                                    
                                    
            #                         if value :
            #                             week_number=key.split(" ")[0][1:]
            #                             print("week Number :",week_number)
            #                             print("Action :",key,":",value)
            #                             if week_number.isdigit():
            #                                 week_number = int(week_number)
            #                                 if value =="NA":
            #                                     value="N/A"
            #                                 action_status=""
            #                                 for choice in ACTION_CHOICE:
            #                                     if value.lower() == choice[1].lower():
            #                                         action_status=choice[0]
                                            
            #                                 if action_status == "":
            #                                     print(f"Error !!! Action Status value :{value} , doesn't not exits in Action Choice ")
            #                                 else :
            #                                         print("Action status :",action_status)
            #                                         get_create_or_update_weekly_report(student_obj=student_obj,
            #                                                                     course_offering_obj=course_offering_obj,
            #                                                                     week_number=week_number,
            #                                                                     engagement_status=None,
            #                                                                     action_status= action_status,
            #                                                                     follow_up_status=None
            #                                                                     )
                                        
            #                             else:
            #                                 print("Invalid week number for Action Status update :", week_number) 
            #                     if "Follow Up" in key:
            #                         print("key :",key)
                                    
                                    
            #                         if value :
            #                             week_number=key.split(" ")[0][1:]
            #                             print("week Number :",week_number)
            #                             print("Follow Up :",key,":",value)
            #                             if week_number.isdigit():
            #                                 week_number = int(week_number)
            #                                 if value =="NA":
            #                                     value="N/A"
            #                                 elif value == "Warning Letter - 1":
            #                                     value ='Warning Letter 1'
            #                                 elif value == "Warning Letter - 2":
            #                                     value ='Warning Letter 2'
                                            
            #                                 follow_up_status=""
            #                                 for choice in FOLLOW_UP_CHOICE:
            #                                     if value.lower() == choice[1].lower():
            #                                         follow_up_status=choice[0]
                                            
            #                                 if follow_up_status == "":
            #                                     print(f"Error !!! Follow Up Status value :{value} , doesn't not exits in Follow Up Choice ")
            #                                 else :
            #                                         print("Follow Up status :",follow_up_status)
            #                                         get_create_or_update_weekly_report(student_obj=student_obj,
            #                                                                     course_offering_obj=course_offering_obj,
            #                                                                     week_number=week_number,
            #                                                                     engagement_status=None,
            #                                                                     action_status= None,
            #                                                                     follow_up_status=follow_up_status
            #                                                                     )
                                        
            #                             else:
            #                                 print("Invalid week number for follow up Status update :", week_number) 
                                        
                                    
                                        
                                            
            #                             #   
                            
            #             # i+=1
                        
                        
                        
            #             # if i == 20:
            #             #     break
                            
                   
                    
            # except Exception as e:
            #  print(f'Error opening attendance file: {e}')
            
            obj.activated = True
            obj.save()
            # Clear the form after successful submission
            bulk_attendance_form = BulkAttendanceUploadForm()
            print("BUlk Student attendance uploaded successfully ")
        
     
    
    context = {
        'bulk_attendance_form': bulk_attendance_form,
       
    }
    
    return render(request, 'upload/upload_bulk_attendance.html', context)