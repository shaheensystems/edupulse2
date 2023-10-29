# views.py
from django.shortcuts import render, redirect,HttpResponse
import csv
from .forms import CSVModelForm
# from .forms import CSVUploadForm
# from .models import UploadFile
from .models import Csv
from program.models import Program,Course
from customUser.models import NewUser,Student
import csv
from django.contrib.auth.hashers import make_password
from datetime import datetime

def handle_date_in_correct_format(date_str):
    print(date_str)
    print("-----------------------------------------")
    if date_str and '/' in date_str and len(date_str) > 7:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            # Handle invalid date format here, if needed
            print(f"Invalid date format: {date_str}")
            return None
            # return datetime.strptime('01/01/2001', "%d/%m/%Y")
    else:
        # Handle the case where date_str does not exist or is not in the expected format
        return None

def updated_or_create_user(data):
    if data['student_id'] and data['student_id'].isdigit():
        try:
            user=NewUser.objects.get(temp_id=data['student_id'])
            # user.username=data['student_id'], # updated username as string ('20220756',) need attention here 
            user.first_name=data['student_fname']
            user.last_name=data['student_lname']
            user.dob=handle_date_in_correct_format(data['student_dob'])
            user.email=data['student_email']
            user.phone=data['student_mobile']
            user.nationality=data['student_nationality']
            user.save()
            # print(user.first_name)
            # print(data['student_id'])
            # print(user.username)
            print(f"user:{user.username} updated successfully")

            
        except NewUser.DoesNotExist:
            new_user=NewUser.objects.create(
                temp_id=data['student_id'],
                username=data['student_id'],
                first_name=data['student_fname'],
                last_name=data['student_lname'],
                dob=handle_date_in_correct_format(data['student_dob']),
                email=data['student_email'],
                phone=data['student_mobile'],
                nationality=data['student_nationality'],
                )
             # Set the user's password
            password = f'WC{data["student_id"]}@{data["student_fname"]}'
            new_user.password = make_password(password)
            new_user.save()
            print(f'user"{new_user.username} cerated successfully')
    else:
        print(f"Ignoring program with code '{data['student_id']}' is not valid ")

def updated_or_create_student(data):
    if data['student_id'] and data['student_id'].isdigit():
        # first cerate and updated user then create and updated student 
        updated_or_create_user(data)

        try:
            student=Student.objects.get(temp_id=data['student_id'])
            
            # student.temp_id=data['student_id'], no changes while updated
            student.email_id=data['student_alternative_email'],
            student.enrollment_status=data['student_enrolment_status'],
            student.passport_number=data['student_passport_number'],
            student.visa_number=data['student_visa_number'],
            # student.visa_expiry_date=handle_date_in_correct_format(data['student_visa_expiry_date']),
            student.save()
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
                course.program.add(linked_program)
            except Program.DoesNotExist:
                # Handle the case where the program doesn't exist
                print(f"Program with code '{data['student_course_code']}' not found")
            course.save()
            print("course updated successfully")
        except Course.DoesNotExist:
            # If not found, create a new program object
            Course.objects.create(temp_id=data['student_course_code'], name=data['student_course_name'])
            print("Course created successfully")
    else:
        print(f"Ignoring Course with code '{data['student_course_code']}' due to spaces in the code, not valid ")

def Upload_file_view(request):
    form = CSVModelForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = CSVModelForm()
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
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
                                "cuor end date":"student_Course_offer_end_date",
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
                student_offer_id = data['student_offer_id']

                # create object as needed for data by importing models here 
                
                # add Program temp- student_program_code, student_program_desc
                update_or_create_program(data=data)
               
                # Print or process the variables
                # print(data['student_program_code'])
                
                # add Course temp- student_program_code, student_program_desc
                update_or_create_course(data=data)

                # add or update Student
                updated_or_create_student(data)


               

        obj.activated = True
        obj.save()

    return render(request, 'upload/upload_file.html', {'form': form})
