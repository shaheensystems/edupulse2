# urls.py
from django.urls import path
from .import views

app_name='upload_file'

urlpatterns = [
    path('', views.Upload_file_view, name='upload_csv'),
    # Add other URL patterns as needed
]