# custom_filters.py
from django import template

register = template.Library()

@register.filter(name='count_poor_performance')
def count_poor_performance(student):
   
        reports = student.weekly_reports.filter(performance='poor')
        # print(f"DEBUG: Reports with poor performance: {reports}")
        return reports.count()