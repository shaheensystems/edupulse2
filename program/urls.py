from django.urls import path,include
from .views import CourseListView,CourseDetailView, CourseOfferingListView,ProgramListView,ProgramDetailView,ProgramOfferingListView,ProgramOfferingDetailView,CourseOfferingDetailView

urlpatterns = [
    path('all-courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<uuid:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses-offering/', CourseOfferingListView.as_view(), name='course_offering_list'),
    path('courses-offering-detail/<uuid:pk>', CourseOfferingDetailView.as_view(), name='course_offering_detail'),
    path('all-program/', ProgramListView.as_view(), name='program_list'),
    path('all-program/<uuid:pk>', ProgramDetailView.as_view(), name='program_detail'),
    path('', ProgramOfferingListView.as_view(), name='program_offering_list'),
    path('program-offering/<uuid:pk>', ProgramOfferingDetailView.as_view(), name='program_offering_detail'),
    
    path('courses-offering/attendance/', include('report.urls')),
]
