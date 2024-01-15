from django.urls import path,include
from attendance.views import AttendanceListView


urlpatterns = [
    path('',AttendanceListView.as_view(),name="all-attendance"),
]
