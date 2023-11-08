from django.urls import path,include
from .views import AttendanceListView,AttendanceCreateView

urlpatterns = [
    
    path('take-attendance/<uuid:pk>/', AttendanceCreateView.as_view(),name='take_attendance'),
    path('<uuid:pk>/', AttendanceListView.as_view(),name='attendance_list'),
]
