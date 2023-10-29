# views.py
from django.shortcuts import render, redirect,HttpResponse
import csv
from .forms import CSVModelForm
# from .forms import CSVUploadForm
# from .models import UploadFile
from .models import Csv
from program.models import Program,Course
import csv


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
                                "client refexternal":"student_ref_external",
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
                                "client passport number":"student_passpport_number",
                                "client country of nationality":"student_nationality",
                                "visa number":"student_visa_number",
                                "visa expiry date":"student_visa_expirty_date",
                                "course code":"student_program_code",
                                "course desc":"student_program_name",
                                "course offer code":"student_program_offer_code",
                                "course offer desc":"student_Program_offer_desc",
                                "cor start date":"student_program_offer_start_date",
                                "cor end date":"student_program_offer_end_date",
                                "unit code":"student_course_code",
                                "unit desc":"student_course_name",
                                "unit offer code":"student_course_offer_code",
                                "unit offer description":"student_course_offer_desc",
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
                    # if program_code is available then update otherwise cerate program 
                # Print or process the variables
                # print(data['student_program_code'])
           
                update_or_create_program(data=data)
                
                # add Course temp- student_program_code, student_program_desc
                update_or_create_course(data=data)
               

        obj.activated = True
        obj.save()

    return render(request, 'upload/upload_file.html', {'form': form})
