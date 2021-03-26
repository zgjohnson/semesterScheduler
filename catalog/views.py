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
from .models import Course, Section


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

    elif request.method == 'POST':

        return render(request, 'homePage.html', {'courses': courses})


@login_required
def viewCourse(request, course_pk):
    courses = get_object_or_404(Course, pk=course_pk)
    section = Section.objects.all()
    return render(request, 'viewCourse.html', {'courses': courses, 'sections': section})


def schedulePage(request):
    return render(request, 'schedulePage.html')