# views.py
from django.shortcuts import render, redirect,HttpResponse
import csv
from .forms import CSVModelForm
# from .forms import CSVUploadForm
# from .models import UploadFile
from .models import Csv
import csv

# def upload_csv(request):
#     if request.method == 'POST':
#         form = CSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             new_file = form.save()
#             csv_file = form.cleaned_data['csv_file']
#             decoded_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
#             for row in reader:
#                 UploadFile.objects.create(
#                     file_name=row['offerid'],
#                     file_path=row['clientofferregid'],
#                     # Add more fields as needed
#                 )
#             return redirect('success_page')  # Redirect to a success page or another URL
#     else:
#         form = CSVUploadForm()

#     return render(request, 'upload/upload_file.html', {'form': form})

def get_validate_index_value(row,variable_name,index_value):
    # Check if the header 'index_value' exists in the CSV
    if index_value>=0:
        variable_name=row[index_value]
    else:
        # Handle the case where the 'offerid' header is not found in the CSV
        print(f"Header '{variable_name}' not found in the CSV.")

def Upload_file_view(request):
    form=CSVModelForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        form.save()
        form=CSVModelForm()
        obj=Csv.objects.get(activated=False)
        with open(obj.file_name.path,'r') as f:
            reader=csv.reader(f)

            header = next(reader, None)
            
            if header is not None:
                # Find the index of the 'offerid' header in the header row
                offer_id_index = header.index('offerid') if 'offerid' in header else -1
                offer_id_index = header.index('clientofferregid') if 'clientofferregid' in header else -1
                student_fname_index = header.index('client first name') if 'client first name' in header else -1
                student_lname_index = header.index('client last name') if 'client last name' in header else -1
                student_dob_index = header.index('client dob') if 'client dob' in header else -1
                student_ref_internal_index = header.index('client refinternal') if 'client refinternal' in header else -1
                student_ref_external_index = header.index('client refexternal') if 'client refexternal' in header else -1
                student_email_index = header.index('client email') if 'client email' in header else -1
                student_alternative_email_index = header.index('client alternative email') if 'client alternative email' in header else -1
                student_mobile_index = header.index('client mobile') if 'client mobile' in header else -1
                student_enrolment_status_index = header.index('enrolment status') if 'enrolment status' in header else -1
                student_address_field1_index = header.index('client post add1') if 'client post add1' in header else -1
                student_address_field2_index = header.index('client post add2') if 'client post add2' in header else -1
                student_address_city_index = header.index('client post suburb') if 'client post suburb' in header else -1
                student_address_postal_code_index = header.index('client post pc') if 'client post pc' in header else -1
                student__index = header.index('client post state') if 'client post state' in header else -1
                student_ethnicity1_index = header.index('nz ethnicity 1') if 'nz ethnicity 1' in header else -1
                student_ethnicity2_index = header.index('nz ethnicity 2') if 'nz ethnicity 2' in header else -1
                student_ethnicity3_index = header.index('nz ethnicity 3') if 'nz ethnicity 3' in header else -1
                student_passport_number_index = header.index('client passport number') if 'client passport number' in header else -1
                student_country_nationality_index = header.index('client country of nationality') if 'client country of nationality' in header else -1
                student_visa_number_index = header.index('visa number') if 'visa number' in header else -1
                student_visa_expiry_date_index = header.index('visa expiry date') if 'visa expiry date' in header else -1
                student_program_code_index = header.index('course code') if 'course code' in header else -1
                student_program_desc_index = header.index('course desc') if 'course desc' in header else -1
                student_program_offer_code_index = header.index('course offer code') if 'course offer code' in header else -1
                student_Program_offer_desc_index = header.index('course offer desc') if 'course offer desc' in header else -1
                student_program_offer_start_date_index = header.index('cor start date') if 'cor start date' in header else -1
                student_program_offer_end_date_index = header.index('cor end date') if 'cor end date' in header else -1
                student__index = header.index('course offer trainer first name') if 'course offer trainer first name' in header else -1
                student__index = header.index('course offer trainer last name') if 'course offer trainer last name' in header else -1
                student_course_code_index = header.index('unit code') if 'unit code' in header else -1
                student_course_desc_index = header.index('unit desc') if 'unit desc' in header else -1
                student_course_offer_code_index = header.index('unit offer code') if 'unit offer code' in header else -1
                student_course_offer_desc_index = header.index('unit offer description') if 'unit offer description' in header else -1
                student_course_offer_start_date_index = header.index('cuor start date') if 'cuor start date' in header else -1
                student_course_offer_end_date_index = header.index('cuor end date') if 'cuor end date' in header else -1
                student_course_offer_outcome_code_index = header.index('outcome code') if 'outcome code' in header else -1
                student_course_offer_outcome_desc_index = header.index('outcome desc') if 'outcome desc' in header else -1
                student__index = header.index('cuor final') if 'cuor final' in header else -1
                student__index = header.index('cuor theory') if 'cuor theory' in header else -1
                student__index = header.index('cuor practical') if 'cuor practical' in header else -1
                student__index = header.index('nz studylink status') if 'nz studylink status' in header else -1
                student__index = header.index('nz studylink reason') if 'nz studylink reason' in header else -1
                student__index = header.index('nz foreign fee') if 'nz foreign fee' in header else -1
                student__index = header.index('nzqa awarding provider') if 'nzqa awarding provider' in header else -1
                student__index = header.index('unit efts factor') if 'unit efts factor' in header else -1
                student__index = header.index('cuor efts factor') if 'cuor efts factor' in header else -1
                student__index = header.index('cuor nzqa result code') if 'cuor nzqa result code' in header else -1
                student__index = header.index('cuor nzqa result desc') if 'cuor nzqa result desc' in header else -1
                student__index = header.index('unit offer location') if 'unit offer location' in header else -1
                student__index = header.index('hasstudentphoto') if 'hasstudentphoto' in header else -1
                student__index = header.index('targetgroupclientofferregid') if 'targetgroupclientofferregid' in header else -1
                student__index = header.index('finalid') if 'finalid' in header else -1
                student_enrollment_id_index = header.index('enrolmentid') if 'enrolmentid' in header else -1
                student__index = header.index('iwi1') if 'iwi1' in header else -1
                student__index = header.index('iwi2') if 'iwi2' in header else -1
                student__index = header.index('iwi3') if 'iwi3' in header else -1
                student__index = header.index('cuor fund source description') if 'cuor fund source description' in header else -1
                student__index = header.index('cuor fund source code') if 'cuor fund source code' in header else -1
                student__index = header.index('forsdr') if 'forsdr' in header else -1
                student__index = header.index('cor target group') if 'cor target group' in header else -1
                student__index = header.index('cuor result code') if 'cuor result code' in header else -1
                student__index = header.index('cuor result desc') if 'cuor result desc' in header else -1
                

                for row in reader:
                    get_validate_index_value(row,offer_id,offer_id_index)
                    print(offer_id)


                    
        obj.activated=True
        obj.save()
    return render(request,'upload/upload_file.html',{'form':form})