from django.contrib import admin
from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from dashboard import views



urlpatterns = [

    path("", views.DashboardView.as_view(),name='home' ),
    path('check_task_status/', views.check_task_status, name='check_task_status'),
    path('check_status_attendance_status_report_chart_data/', views.check_status_attendance_status_report_chart_data, name='check_status_attendance_status_report_chart_data'),

    
]
