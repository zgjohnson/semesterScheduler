"""semesterScheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from catalog.views import MyRegistrationView
from catalog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', MyRegistrationView.as_view()),
    path('accounts/', include('registration.backends.default.urls')),

    #Catalog pages
    path('', views.homePage, name='homePage'),
    path('schedule/', views.schedulePage, name='schedulePage'),
    path('course/<int:course_pk>', views.viewCourse, name='viewCourse'),
    path('possible_courses/', views.designatedCourses, name='designatedCourses'),
    path('possible_courses/<int:pk>', views.delDesignatedCourse, name='delDesignatedCourse'),
    path('reserved_times/', views.reservedTimes, name='reservedTimes'),
    path('reserved_times/<int:pk>', views.delReservedTime, name='delReservedTime'),
    path('schedule_generator/', views.scheduleGenerator, name='scheduleGenerator')
]
