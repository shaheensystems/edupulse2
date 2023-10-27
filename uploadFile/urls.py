# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    # Add other URL patterns as needed
]