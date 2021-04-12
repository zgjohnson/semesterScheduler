from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from registration.backends.default.views import RegistrationView

from django.contrib.auth.models import Group
from .forms import MyRegistrationForm
from django.contrib.auth.hashers import make_password
from registration.models import RegistrationManager
from registration.models import RegistrationProfile
from registration.models import send_email
from .models import Course, DesignatedCourses, ReservedTime, Section, Period
from .forms import DesignatedCoursesForm, ReservedTimeForm
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
    dc_list = DesignatedCourses.objects.filter(user=current_user)

    if request.method == 'GET':

        return render(request, 'designatedCourses.html', {'courses': courses, 'designatedCourses': dc_list})

    else:

        form = DesignatedCoursesForm(request.POST)
        if form.is_valid():
            dc_entry, created = DesignatedCourses.objects.get_or_create(user=current_user)
            dc_entry.designated_courses.add(*form.cleaned_data['choices'])

        return render(request, 'designatedCourses.html', {'courses': courses, 'designatedCourses': dc_list})


@login_required
def reservedTimes(request):
    current_user = request.user

    try:
        rt = ReservedTime.objects.filter(user=current_user)

    except ObjectDoesNotExist:
        rt = None

    if request.method == 'GET':
        return render(request, 'reservedTimes.html', {'reservedTimes': rt, 'form': ReservedTimeForm()})

    else:
        form = ReservedTimeForm(request.POST)
        new_rt = form.save(commit=False)
        new_rt.user = current_user
        new_rt.save()
        return render(request, 'reservedTimes.html', {'reservedTimes': rt, 'form': ReservedTimeForm()})


@login_required
def delReservedTime(request, pk):
    rt = get_object_or_404(ReservedTime, pk=pk)

    if request.method == 'POST':
        rt.delete()
        return redirect('reservedTimes')


@login_required
def scheduleGenerator(request):
    current_user = request.user
    try:
        rt = ReservedTime.objects.filter(user=current_user)

    except ObjectDoesNotExist:
        rt = None

    dc = DesignatedCourses.objects.filter(user=current_user)

    periods = Period.objects.all()
    possible_periods = []
    for period in periods:
        possible_periods.append(period)

    for reservedTime in rt:
        print(reservedTime, reservedTime.reserved_Day, reservedTime.start_Time, reservedTime.end_Time)
        print(possible_periods)
        for period in periods:

            if reservedTime.reserved_Day in period.meeting_day:
                if reservedTime.start_Time <= period.start_Time and period.end_Time <= reservedTime.end_Time:
                    possible_periods.remove(period)
                elif period.start_Time <= reservedTime.start_Time and reservedTime.end_Time <= period.end_Time:
                    possible_periods.remove(period)
                elif reservedTime.start_Time <= period.start_Time <= reservedTime.end_Time or reservedTime.start_Time <= period.end_Time <= reservedTime.end_Time:
                    possible_periods.remove(period)
    print('These are the possible periods')
    print(possible_periods)

    for user in dc:
        pc = user.designated_courses.all()

    if request.method == 'GET':
        return render(request, 'scheduleGenerator.html', {'reservedTimes': rt, 'possibleCourses': pc})

    else:
        form = DesignatedCoursesForm(request.POST)
        possible_courses = []

        if form.is_valid():

            for course in form.cleaned_data['choices']:
                possible_courses.append(course)

        print(possible_courses)

        return render(request, 'scheduleGenerator.html', {'reservedTimes': rt, 'possibleCourses': pc})
