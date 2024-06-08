import django_filters
from django import forms
from django_filters import widgets as filters_widgets
from report.models import Attendance
from program.models import Program

class TailwindChoiceWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        # attrs = {'class': 'flex justify-left px-8 py-1 text-gray-500 border border-red-800 text-sm'}
        if attrs is None:
            attrs = {}
        attrs.update({
            'class': 'flex justify-left px-8 py-1 text-gray-500 border border-red-800',
            'onchange': 'this.form.submit()'  # Automatically submit the form on change
        })
        super().__init__(attrs, choices)

class AttendanceEngagementReportFilter(django_filters.FilterSet):
    week_no_choices = [(week_no, f"Week {week_no}") for week_no in Attendance.objects.values_list('week_no', flat=True).distinct()]
    session_no_choices = [(session_no, f"Session {session_no}") for session_no in Attendance.objects.values_list('session_no', flat=True).distinct()]
    program_choices = [(program.id, program.name) for program in Program.objects.all()]
    
    # program_offering__program = django_filters.ChoiceFilter(
    #     widget=TailwindChoiceWidget(),
    #     choices=program_choices,
    #     empty_label="Select Program"
    # )
   
    week_no = django_filters.ChoiceFilter(
        widget=TailwindChoiceWidget(),
        choices=week_no_choices,
        empty_label="Select Week",
      
    )
    session_no = django_filters.ChoiceFilter(
        widget=TailwindChoiceWidget(),
        choices=session_no_choices,
        empty_label="Select Session"
    )
    course_offering__student_enrollments__program_offering__program=django_filters.ChoiceFilter(
        widget=TailwindChoiceWidget(),
        choices=program_choices,
        empty_label="Select Program",
      
    )
    class Meta:
        model=Attendance
        fields=['course_offering__student_enrollments__program_offering__program','week_no','session_no']