from django.urls import path
from .views import CourseListView, CourseOfferingListView,ProgramListView,ProgramDetailView,ProgramOfferingListView,ProgramOfferingDetailView

urlpatterns = [
    path('all-courses/', CourseListView.as_view(), name='course_list'),
    path('courses-offering/', CourseOfferingListView.as_view(), name='course_offering_list'),
    path('all-program/', ProgramListView.as_view(), name='program_list'),
    path('all-program/<uuid:pk>', ProgramDetailView.as_view(), name='program_detail'),
    path('', ProgramOfferingListView.as_view(), name='program_offering_list'),
    path('program-offering/<uuid:pk>', ProgramOfferingDetailView.as_view(), name='program_offering_detail'),
    # path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
]
