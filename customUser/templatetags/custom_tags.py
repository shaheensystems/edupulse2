# custom_filters.py
from django import template
from django.contrib.auth.models import Group, User
from django.core.cache import cache

register = template.Library()

@register.filter(name='count_poor_performance')
def count_poor_performance(student):
   
        reports = student.weekly_reports.filter(performance='poor')
        # print(f"DEBUG: Reports with poor performance: {reports}")
        return reports.count()

# @register.filter(name='user_belongs_to_group')
# def user_belongs_to_group(user,group_name):

#         return user.groups.filter(name=group_name).exists()



# cache method 
@register.filter(name='user_belongs_to_group')
def user_belongs_to_group(user, group_name):
    cache_key = f'user_group_{user.id}_{group_name}'
#     print(f"cache key :{cache_key}")
    result = cache.get(cache_key)
#     print(f" result :{result}")
    if result is None:
        result = user.groups.filter(name=group_name).exists()
        # cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
        cache.set(cache_key, result, timeout=3600)  # Cache for 60 sec
        
#     print(f" result after checking:{result}")
    return result

@register.filter(name='get')
def get(dictionary, key):
    return dictionary.get(key, None)
