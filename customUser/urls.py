from django.urls import path
from customUser.views import UserLoginView,UserLogOutView

urlpatterns = [
    path("login/",UserLoginView.as_view(),name="user-login"),
    path("logout/",UserLogOutView.as_view(),name="user-logout"),
]
