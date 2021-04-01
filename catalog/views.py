from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from registration.backends.default.views import RegistrationView

from django.contrib.auth.models import Group
from .forms import MyRegistrationForm
from django.contrib.auth.hashers import make_password
from registration.models import RegistrationManager
from registration.models import RegistrationProfile
from registration.models import send_email
from .models import Course, Section, DesignatedCourses
from .forms import DesignatedCoursesForm
from django.core.exceptions import ObjectDoesNotExist


class MyRegistrationView(RegistrationView):
    def register(self, form):
        user = super().register(form)

        data = form.cleaned_data

        if data['access_requested'] == 'A':
            user.is_staff = True
            staff_group = Group.objects.get(name='Staff')
            staff_group.user_set.add(user)

        elif data['access_requested'] == 'R':
            user.is_staff = True
            user.is_superuser = True

        user.save()


@login_required
def homePage(request):
    courses = Course.objects.all()

    if request.method == 'GET':

        return render(request, 'homePage.html', {'courses': courses})

    else:

        return render(request, 'homePage.html', {'courses': courses})


@login_required
def viewCourse(request, course_pk):
    courses = get_object_or_404(Course, pk=course_pk)
    section = Section.objects.all()
    return render(request, 'viewCourse.html', {'courses': courses, 'sections': section})


@login_required
def schedulePage(request):
    return render(request, 'schedulePage.html')


@login_required
def designatedCourses(request):

    courses = Course.objects.all()
    current_user = request.user

    if request.method == 'GET':

        return render(request, 'designatedCourses.html', {'courses': courses})

    else:

        form = DesignatedCoursesForm(request.POST)
        if form.is_valid():
            dc_entry, created = DesignatedCourses.objects.get_or_create(user=current_user)
            dc_entry.designated_courses.add(*form.cleaned_data['choices'])

        return render(request, 'designatedCourses.html', {'courses': courses})