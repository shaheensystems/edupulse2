# forms.py
from django import forms
from .models import Attendance  # Import your Attendance model

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student','program_offering','course_offering','is_present','attendance_date','attendance_date','remark']
        # You can include other fields as needed
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['program_offering'].widget = forms.HiddenInput()
        # self.fields['course_offering'].widget = forms.HiddenInput()

    # Optionally, you can add custom validation or widgets here
