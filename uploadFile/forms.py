# forms.py
from django import forms
# from uploadFile.models import UploadFile,Csv
from uploadFile.models import Csv, AttendanceUpload, CanvasStatsUpload

# class CSVUploadForm(forms.Form):
#     csv_file = forms.FileField(label='Select a CSV File')

#     class Meta:
#         model = UploadFile
#         fields = ['file_name', 'file_path']

class CSVModelForm(forms.ModelForm):
  
    class Meta:
        model = Csv
        fields = ("file_name",)

class AttendanceUploadForm(forms.ModelForm):
  
    class Meta:
        model = AttendanceUpload
        fields = ("file_name",)

class CanvasStatsUploadForm(forms.ModelForm):
  
    class Meta:
        model = CanvasStatsUpload
        fields = ("file_name",)

        