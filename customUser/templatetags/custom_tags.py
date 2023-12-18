# custom_filters.py
from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='count_poor_performance')
def count_poor_performance(student):
   
        reports = student.weekly_reports.filter(performance='poor')
        # print(f"DEBUG: Reports with poor performance: {reports}")
        return reports.count()

@register.filter(name='user_belongs_to_group')
def user_belongs_to_group(user,group_name):
        return user.groups.filter(name=group_name).exists()

@register.filter(name='get')
def get(dictionary, key):
    return dictionary.get(key, None)
