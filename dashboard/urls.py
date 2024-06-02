from django.contrib import admin
from django.conf import settings
from django.urls import path,include
from django.conf.urls.static import static
from dashboard import views


urlpatterns = [
    path("", views.home,name='home' ),
    path("2/", views.DashboardView.as_view(),name='home2' ),
    path('check_task_status/', views.check_task_status, name='check_task_status'),
   
    
    
]
