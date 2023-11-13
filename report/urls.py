from django.urls import path,include
from .views import AttendanceListView,AttendanceCreateView, mark_attendance, WeeklyReportView,edit_weekly_report

urlpatterns = [
    
    path('take-attendance/<uuid:pk>/', AttendanceCreateView.as_view(),name='take_attendance'),
    path('<uuid:pk>/', AttendanceListView.as_view(),name='attendance_list'),
    path('create-attendance/<uuid:pk>/', mark_attendance,name='create-attendance'),
    path('weekly-report/<uuid:pk>/', WeeklyReportView.as_view(),name='weekly_report_list'),
    path('weekly-report/<uuid:pk>/edit/<int:week_number>', edit_weekly_report,name='edit_weekly_report'),
    
]
