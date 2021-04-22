from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from registration.backends.default.views import RegistrationView
from itertools import product, chain, combinations
from django.contrib.auth.models import Group
from .models import Course, DesignatedCourses, ReservedTime, Section, Period, ScheduledCourses, ScheduleOption, Schedule
from .forms import DesignatedCoursesForm, ReservedTimeForm
from django.core.exceptions import ObjectDoesNotExist


# Custom Registration View that extends the one included in Registration-Redux
class MyRegistrationView(RegistrationView):
    def register(self, form):  # Register function.
        user = super().register(form)  # Creates a user from the information from the form passed in.
        data = form.cleaned_data    # Cleans the forms data.

        if data['access_requested'] == 'A':  # Checks to see if user Registered as an Admin
            user.is_staff = True    # Sets the users is_staff field to true and allows the user admin privileges.
            staff_group = Group.objects.get(name='Staff')     # Creates a QuerySet containing the group objects named Staff.
            staff_group.user_set.add(user)  # Adds the user to the Staff group so they can manage the database.

        elif data['access_requested'] == 'R':   # Check to see if user Registered as a Root user.
            user.is_staff = True    # Sets the users is_staff field to true and allows the user admin privileges.
            user.is_superuser = True    # Sets the users is_superuser field to true and allows the user root privileges.

        user.save()  # Saved the user instance.


@login_required # Requires user to be logged in
# Defines the Catalog Home Page
def homePage(request):
    courses = Course.objects.all()  # Creates a QuerySet of all the Courses in the Catalog
    # passes the request, the html page and a dictionary containing the course queryset
    return render(request, 'homePage.html', {'courses': courses})


@login_required  # Requires user to be logged in
# Defines the viewCourse page showing the sections for a given course.
def viewCourse(request, course_pk):  # Takes in the Request and the pk of the course

    # gets the course object associated with the pk and or displays the 404 page if it DNE.
    courses = get_object_or_404(Course, pk=course_pk)

    section = Section.objects.all()  # QuerySet of all Section objects.

    return render(request, 'viewCourse.html', {'courses': courses, 'sections': section})


@login_required  # Requires user to be logged in
def schedulePage(request):
    return render(request, 'schedulePage.html')


@login_required  # Requires user to be logged in
# Function that returns a render for the Possible Course page
def designatedCourses(request):
    courses = Course.objects.all()  # Creates a QuerySet of all the Courses in the Catalog
    current_user = request.user  # Creates an instance of user with the current user as parameters.
    dc_list = DesignatedCourses.objects.filter(user=current_user)  # QuerySet of the DesignatedCourse object that belongs to the current User.

    if request.method == 'GET':  # If the request is a GET request
        # passes the request, the html page and a dictionary containing both the course queryset and the designatedCourses queryset.
        return render(request, 'designatedCourses.html', {'courses': courses, 'designatedCourses': dc_list})

    else:  # The request is a POST request
        form = DesignatedCoursesForm(request.POST)  # Creates a form from the DCForm template with the information from the request passed in.
        if form.is_valid():  # Checks to see if the information from the form is valid
            dc_entry, created = DesignatedCourses.objects.get_or_create(user=current_user)  # This creates a new DC object if there is not already one connected to the current user.
            dc_entry.designated_courses.add(*form.cleaned_data['choices'])  # This adds the courses chosen in the form to the users DC.designated_courses relationship.
        # passes the request, the html page and a dictionary containing both the course queryset and the designatedCourses queryset.
        return render(request, 'designatedCourses.html', {'courses': courses, 'designatedCourses': dc_list})


@login_required  # Requires user to be logged in
# Function to delete the Possible Course
def delDesignatedCourse(request, pk):
    dc = DesignatedCourses.objects.get(user=request.user)  # Get all DC associated with the current user.
    course = Course.objects.get(pk=pk)  # Get course with matching primary key.

    if request.method == 'POST':
        dc.designated_courses.remove(course)    # Remove selected course reference from the many to many relationship in DC
        return redirect('designatedCourses')    # Redirect to the same page


@login_required  # Requires user to be logged in
# Function to display users Reserved Tines
def reservedTimes(request):
    current_user = request.user  # Gets current user

    try:    # Queryset to see if there are any RT for the user
        rt = ReservedTime.objects.filter(user=current_user)
    except ObjectDoesNotExist:  # If there are none set rt to none
        rt = None

    if request.method == 'GET':
        return render(request, 'reservedTimes.html', {'reservedTimes': rt, 'form': ReservedTimeForm()})

    else:  # Request Post.
        form = ReservedTimeForm(request.POST)  # Sets the form instance to ReservedTimeForm with the information from the Post request
        new_rt = form.save(commit=False)  # Creates a new rt object with the info on the form. Doesn't commit because the user is not set yet
        new_rt.user = current_user  # Sets the current user
        new_rt.save()  # Saves the new object
        return render(request, 'reservedTimes.html', {'reservedTimes': rt, 'form': ReservedTimeForm()})


@login_required  # Requires user to be logged in
# Function to Delete a selected RT
def delReservedTime(request, pk):
    rt = get_object_or_404(ReservedTime, pk=pk)  # Gets the RT object or returns a 404 page

    if request.method == 'POST':
        rt.delete()  # Deletes the RT object
        return redirect('reservedTimes')


@login_required  # Requires user to be logged in
# Function to Generate Schedule Options
def scheduleGenerator(request):
    current_user = request.user  # Sets current user

    try:  # Tries to run a QuerySet to get all the RT objects associated with the user
        rt = ReservedTime.objects.filter(user=current_user)
    except ObjectDoesNotExist:  # If object DNE sets rt to none
        rt = None

    try:  # Tries to run a QuerySet to get all the SO objects associated with the user
        schedule_options = ScheduleOption.objects.filter(user=current_user)
    except ObjectDoesNotExist:  # If object DNE sets schedule_options to none
        schedule_options = None

    try:  # Tries to run a QuerySet to get all the DC objects associated with the user
        pc = DesignatedCourses.objects.get(user=current_user).designated_courses.all()
    except ObjectDoesNotExist:  # If object DNE sets pc to none
        pc = None

    periods = Period.objects.all()  # QuerySet to get all period objects
    possible_periods = []  # Empty list used to store possible periods
    possible_sections = []  # Empty list used to store possible sections

    for period in periods:  # Adds every period to the list
        possible_periods.append(period)

    # Creates a list of periods that do not overlap any of the users rt
    for reservedTime in rt:  # Loops over every rt related to the user
        for period in periods:  # Loops over every period object to compare to every rt object
            if reservedTime.reserved_Day in period.meeting_day:  # If the reserved time is on the same day as the period check to see if the times cross over
                if reservedTime.start_Time <= period.start_Time and period.end_Time <= reservedTime.end_Time:  # If period is between rt start and end time
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:
                        continue
                elif period.start_Time <= reservedTime.start_Time and reservedTime.end_Time <= period.end_Time:  # If rt is between period start and end time
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:
                        continue
                    # If The period start time or period end time is between rt start and end time
                elif reservedTime.start_Time <= period.start_Time <= reservedTime.end_Time or reservedTime.start_Time <= period.end_Time <= reservedTime.end_Time:
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:
                        continue

    if request.method == 'GET':
        # Displays users reserved times, possible courses, and schedule options
        return render(request, 'scheduleGenerator.html',
                      {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options})

    else:
        ScheduleOption.objects.all().delete()  # Clears previous Schedule options
        form = DesignatedCoursesForm(request.POST)  # Retrieves DC from form chosen by user
        course_sections = {}  # Empty dictionary to hold
        course_count = 0

        if form.is_valid():
            for course in form.cleaned_data['choices']:
                course_count += 1
                sections = Section.objects.filter(course=course)
                for section in sections:
                    possible_sections.append(section)

        if course_count == 0:
            error = "Please choose from the Possible Courses"
            return render(request, 'scheduleGenerator.html',
                          {'reservedTimes:': rt, 'possibleCourses': pc, 'error': error})

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

        permutations_dicts = []

        def all_combinations(lst):
            return chain(*[combinations(lst, i + 1) for i in range(len(lst))])

        for comb in all_combinations(course_sections):
            for prod in product(*(course_sections[k] for k in comb)):
                use = dict(zip(comb, prod))
                if len(use) == course_count:
                    permutations_dicts.append(use)


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
            schedule_option = ScheduleOption.objects.create(user=current_user)
            for k, v in schedules[i].items():
                scheduled_course = ScheduledCourses.objects.create(section_id=k, period_id=v, groupNumber=i)
                scheduled_course.save()
                schedule_option.scheduled_Courses.add(scheduled_course)
                schedule_option.save()

        schedule_options = ScheduleOption.objects.filter(user=current_user)

        return render(request, 'scheduleGenerator.html',
                      {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options})


@login_required  # Requires user to be logged in
def saveSchedule(request, pk):
    if request.method == 'POST':
        schedule_option = ScheduleOption.objects.get(pk=pk)
        saved_schedule = Schedule.objects.create(user=request.user)
        for course in schedule_option.scheduled_Courses.all():
            saved_schedule.savedScheduledCourse.add(course)

        saved_schedule.save()
        return redirect('scheduleGenerator')


@login_required  # Requires user to be logged in
def savedSchedules(request):
    try:
        saved_schedules = Schedule.objects.filter(user=request.user)
    except ObjectDoesNotExist:
        saved_schedules = None

    print(saved_schedules)

    if request.method == 'GET':
        return render(request, 'savedSchedules.html', {'saved_schedules': saved_schedules})


@login_required
def delSchedules(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return redirect('savedSchedules')
