# urls.py
from django.urls import path
from .import views

app_name='upload_file'

urlpatterns = [
    path('', views.Upload_file_view, name='upload_csv'),
    path('bulk_attendance_upload',views.Upload_bulk_attendance_view, name='upload-bulk-attendance')
    # Add other URL patterns as needed
]