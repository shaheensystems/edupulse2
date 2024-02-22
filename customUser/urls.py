from django.urls import path
from customUser.views import UserLoginView,UserLogOutView, AllStudentsView, AllStudentsAtRiskView, StudentDetailView
from django.urls import reverse_lazy

urlpatterns = [
    path("login/",UserLoginView.as_view(),name="user-login"),
    path("logout/",UserLogOutView.as_view(),name="user-logout"),
    path("students/",AllStudentsView.as_view(),name="students-list"),
    path("students/<uuid:pk>",StudentDetailView.as_view(),name="student-details"),
    path('all-students-at-risk/', AllStudentsAtRiskView.as_view(), name='all-students-at-risk'),
   
]
