# views.py
from django.shortcuts import render, redirect
import csv
from .forms import CSVUploadForm
from .models import UploadFile

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save()
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                UploadFile.objects.create(
                    file_name=row['offerid'],
                    file_path=row['clientofferregid'],
                    # Add more fields as needed
                )
            return redirect('success_page')  # Redirect to a success page or another URL
    else:
        form = CSVUploadForm()

    return render(request, 'upload/upload_file.html', {'form': form})
