from django import forms
from datetime import datetime, timedelta



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

