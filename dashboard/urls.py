from django.contrib import admin
from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from dashboard import views



urlpatterns = [

    path("", views.DashboardView.as_view(),name='dashboard' ),
    path("celery-dashboard/", views.DashboardCeleryView.as_view(),name='home-celery' ),
    path('check_task_status/', views.check_task_status, name='check_task_status'),
    path('check_status_attendance_status_report_chart_data/', views.check_status_attendance_status_report_chart_data, name='check_status_attendance_status_report_chart_data'),
    path('filter_attendances/<int:pk>/', views.FilterAttendancesAjaxView.as_view(), name='filter_attendances'),
    path('load_course_offering_data/<uuid:pk>/', views.LoadCourseOfferingDataAjaxView.as_view(), name='load_course_offering_data'),

    
]
