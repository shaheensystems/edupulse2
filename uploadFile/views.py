# views.py
from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
import csv
from .forms import CSVModelForm,AttendanceUploadForm, CanvasStatsUploadForm
# from .forms import CSVUploadForm
# from .models import UploadFile
from .models import Csv,CanvasStatsUpload
from report.models import Attendance,WeeklyReport, StudentEnrollment
from customUser.models import Student
from program.models import Program,Course,ProgramOffering,CourseOffering
from customUser.models import NewUser,Student,Campus, Ethnicity, StudentFundSource
import csv
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.urls import reverse

from report.views import get_week_number
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

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
            if data['student_id']=='20220228':
                print(linked_course_offering)
                print(linked_program_offering)
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

                # Access the data using the variable names
                # student_offer_id = data['student_offer_id']

                # create object as needed for data by importing models here 
                
                # add Program temp- student_program_code, student_program_desc
                update_or_create_program(data=data)
               
                # Print or process the variables
                # print(data['student_program_code'])
                
                # add Course temp- student_program_code, student_program_desc
                update_or_create_course(data=data)

                # add or update Student
                updated_or_create_student(data)

                # add course and program offering after creating student 
                update_or_create_course_offering(data)
                update_or_create_program_offering(data)
                update_or_create_student_enrollment(data)

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

    pass      

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