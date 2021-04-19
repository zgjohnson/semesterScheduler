from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from registration.backends.default.views import RegistrationView
from collections import defaultdict
from itertools import product, chain, combinations
from django.contrib.auth.models import Group
from .forms import MyRegistrationForm
from django.contrib.auth.hashers import make_password
from registration.models import RegistrationManager
from registration.models import RegistrationProfile
from registration.models import send_email
from .models import Course, DesignatedCourses, ReservedTime, Section, Period, ScheduledCourses, ScheduleOption
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
    possible_sections = []
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

    for user in dc:
        pc = user.designated_courses.all()

    if request.method == 'GET':
        return render(request, 'scheduleGenerator.html', {'reservedTimes': rt, 'possibleCourses': pc})

    else:

        ScheduleOption.objects.all().delete()
        ScheduledCourses.objects.all().delete()
        form = DesignatedCoursesForm(request.POST)
        course_sections = {}
        course_count = 0

        if form.is_valid():
            for course in form.cleaned_data['choices']:
                course_count += 1
                sections = Section.objects.filter(course=course)
                for section in sections:
                    possible_sections.append(section)

        if course_count == 0:
            error = "Please choose from the Possible Courses"
            return render(request, 'scheduleGenerator.html', {'reservedTimes:': rt, 'possibleCourses': pc, 'error': error})

        for section in possible_sections:
            for period in possible_periods:
                if period in section.periods.all():
                    course_sections[section.id] = course_sections.get(section.id, []) + [period.id]


        # all_courses = sorted(course_sections)
        # combinations = it.product(*(course_sections[Name] for Name in all_courses))
        # print(list(combinations))
        # keys, values = zip(*course_sections.items())
        # permutations_dicts = [dict(zip(keys, v)) for v in product(*values)]
        # print(permutations_dicts)
        perm2 = []
        permutations_dicts = []

        def all_combinations(lst):
            return chain(*[combinations(lst, i + 1) for i in range(len(lst))])

        for comb in all_combinations(course_sections):
            for prod in product(*(course_sections[k] for k in comb)):
                use = dict(zip(comb, prod))
                if len(use) == course_count:
                    permutations_dicts.append(use)
                    perm2.append(use)


        items_to_remove = set()
        for i in range(len(permutations_dicts)):
            temp_dictionary = permutations_dicts[i]
            temp_dictionary2 = permutations_dicts[i]
            for k, v in temp_dictionary.items():
                for k2, v2 in temp_dictionary2.items():
                    if k == k2:
                        continue
                    else:
                        per1 = Period.objects.get(id=v)
                        per2 = Period.objects.get(id=v2)
                        sec1 = Section.objects.get(id=k)
                        sec2 = Section.objects.get(id=k2)
                        if sec1.course.course_Title == sec2.course.course_Title:
                            items_to_remove.add(i)
                        if per1.meeting_day in per2.meeting_day or per2.meeting_day in per1.meeting_day:
                            if per1.start_Time <= per2.start_Time and per2.end_Time <= per1.end_Time:
                                items_to_remove.add(i)
                                break
                            elif per2.start_Time <= per1.start_Time and per1.end_Time <= per2.end_Time:
                                items_to_remove.add(i)
                                break
                            elif per1.start_Time <= per2.start_Time <= per1.end_Time or per1.start_Time <= per2.end_Time <= per1.end_Time:
                                items_to_remove.add(i)
                                break
        schedules = []
        for i in range(len(permutations_dicts)):
            if i not in items_to_remove:
                schedules.append(permutations_dicts[i])

        for i in range(len(schedules)):
            schedule_Option = ScheduleOption.objects.create(user=current_user)
            for k, v in schedules[i].items():
                scheduled_Course = ScheduledCourses.objects.create(section_id=k, period_id=v, groupNumber=i)
                scheduled_Course.save()
                schedule_Option.scheduled_Courses.add(scheduled_Course)
                schedule_Option.save()

        schedule_Options = ScheduleOption.objects.filter(user=current_user)

        return render(request, 'scheduleGenerator.html',
                      {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_Options})
