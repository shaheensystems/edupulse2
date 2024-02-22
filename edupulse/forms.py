from django import forms
from datetime import datetime, timedelta
from program.models import CourseOffering
from customUser.models import Student
from django.db.models import Prefetch
from report.models import WeeklyReport



class DateFilterForm(forms.Form):
    default_start_date = datetime(datetime.now().year - 1, 1, 1).strftime('%Y-%m-%d')
    default_end_date = datetime.now().strftime('%Y-%m-%d')
   
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date','value':default_start_date}),
        required=False
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date','value':default_end_date}),
        required=False
    )

class ManageAttendanceFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Retrieve the user from kwargs
        super(ManageAttendanceFilterForm, self).__init__(*args, **kwargs)
        
        # Filter queryset for course_offering based on the user's staff attribute
        if user:
            self.fields['course_offering'].queryset = CourseOffering.objects.prefetch_related('teacher','student','teacher__staff','attendances',\
                                                                                              Prefetch('weekly_reports', queryset=WeeklyReport.objects.prefetch_related('sessions'))\
                                                                                              ).filter(teacher__staff=user)
            
        
            # Populate week number choices dynamically
            # self.fields['week_number'] = forms.ChoiceField(choices=[], required=True)
       
        # Initialize student field queryset as empty
        self.fields['student'].queryset = Student.objects.none()
        
    # Hardcoded week number choices
    week_number = forms.ChoiceField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], required=True)

    course_offering = forms.ModelChoiceField(queryset=CourseOffering.objects.none())  # Initialize as empty queryset
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)

    def set_student_choices(self, course_offering_id):
        if course_offering_id:
            # Get the selected course offering
            course_offering = CourseOffering.objects.get(pk=course_offering_id)
            
            # Set queryset for student field based on the selected course offering
            self.fields['student'].queryset = course_offering.student.all()