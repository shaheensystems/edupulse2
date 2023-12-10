from django.urls import path
from customUser.views import UserLoginView,UserLogOutView, AllStudentsView, AllStudentsAtRiskView


urlpatterns = [
    path("login/",UserLoginView.as_view(),name="user-login"),
    path("logout/",UserLogOutView.as_view(),name="user-logout"),
    path("students/",AllStudentsView.as_view(),name="all-students"),
     path('all-students-at-risk/', AllStudentsAtRiskView.as_view(), name='all-students-at-risk'),
   
]
