from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from registration.backends.default.views import RegistrationView
from itertools import product, chain, combinations
from django.contrib.auth.models import Group
from .models import Course, DesignatedCourses, ReservedTime, Section, Period, ScheduledCourses, ScheduleOption, Schedule
from .forms import DesignatedCoursesForm, ReservedTimeForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


# Custom Registration View that extends the one included in Registration-Redux
class MyRegistrationView(RegistrationView):
    def register(self, form):  # Register function.
        user = super().register(form)  # Creates a user from the information from the form passed in.
        data = form.cleaned_data    # Cleans the forms data.

        if data['access_requested'] == 'A':  # Checks to see if user Registered as an Admin
            # Adds the user to the group that is awaiting approval for Admin Privileges
            admin_awaiting_approval = Group.objects.get(name='Admin_Awaiting_Approval')
            admin_awaiting_approval.user_set.add(user)
            # user.is_staff = True    # Sets the users is_staff field to true and allows the user admin privileges.
            # staff_group = Group.objects.get(name='Staff')     # Creates a QuerySet containing the group objects named Staff.
            # staff_group.user_set.add(user)  # Adds the user to the Staff group so they can manage the database.

        elif data['access_requested'] == 'R':   # Check to see if user Registered as a Root user.
            # Adds the user to the group that is awaiting approval for Root Privileges
            root_awaiting_approval = Group.objects.get(name='Root_Awaiting_Approval')
            root_awaiting_approval.user_set.add(user)
            # user.is_staff = True    # Sets the users is_staff field to true and allows the user admin privileges.
            # user.is_superuser = True    # Sets the users is_superuser field to true and allows the user root privileges.

        user.save()  # Saved the user instance.


@login_required  # Requires user to be logged in
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

    rt = ReservedTime.objects.filter(user=current_user)

    schedule_options = ScheduleOption.objects.filter(user=current_user)



    try:  # Tries to run a QuerySet to get all the DC objects associated with the user
        pc = DesignatedCourses.objects.get(user=current_user).designated_courses.all()
    except ObjectDoesNotExist:  # If object DNE sets pc to none
        pc = None

    periods = Period.objects.all()  # QuerySet to get all period objects
    possible_periods = []  # Empty list used to store possible periods
    possible_sections = []  # Empty list used to store possible sections
    permutations_dicts = []  # List used to store the possible section/period permutations
    items_to_remove = set()  # Set of items to remove from the list of possible section/period permutations. Used set here because items will not repeat.
    schedules = []  # List of dictionaries of schedules with section.id as keys and period.id as values

    for period in periods:  # Adds every period to the list
        possible_periods.append(period)

    # Creates a list of periods that do not overlap any of the users rt
    for reservedTime in rt:  # Loops over every rt related to the user
        for period in periods:  # Loops over every period object to compare to every rt object
            if reservedTime.reserved_Day in period.meeting_day:  # If the reserved time is on the same day as the period check to see if the times cross over
                # If period is between rt start and end time
                if reservedTime.start_Time <= period.start_Time and period.end_Time <= reservedTime.end_Time:
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:  # If the period has already been removed skip it.
                        continue
                # If rt is between period start and end time
                elif period.start_Time <= reservedTime.start_Time and reservedTime.end_Time <= period.end_Time:
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:  # If the period has already been removed skip it.
                        continue
                # If The period start time or period end time is between rt start and end time
                elif reservedTime.start_Time <= period.start_Time <= reservedTime.end_Time or reservedTime.start_Time <= period.end_Time <= reservedTime.end_Time:
                    try:
                        possible_periods.remove(period)  # remove period from list
                    except ValueError:  # If the period has already been removed skip it.
                        continue

    if request.method == 'GET':

        if schedule_options.count() == 0:
            error = "Please click the Generate Schedules button"
            return render(request, 'scheduleGenerator.html',
                          {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options,
                           'error': error})
        # Displays users reserved times, possible courses, and schedule options
        return render(request, 'scheduleGenerator.html',
                      {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options})

    else:
        ScheduleOption.objects.all().delete()  # Clears previous Schedule options from the screen
        form = DesignatedCoursesForm(request.POST)  # Retrieves DC from form chosen by user
        course_sections = {}  # Empty dictionary to hold Section id as key and a list of period ids associated with that section as the value
        course_count = 0    # Tracks the number of courses the user has chosen.

        if form.is_valid():  # Checks if the form data is valid
            for course in form.cleaned_data['choices']:  # Loops through the courses chosen
                course_count += 1  # Counts the Courses
                sections = Section.objects.filter(course=course)  # QuerySet to find all the section objects related to that course
                for section in sections:    # Loop through all the sections
                    possible_sections.append(section)   # Add those sections to the list

        if course_count == 0:   # If the user did not choose any courses
            error = "Please choose from the Possible Courses"   # Error message to be displayed
            return render(request, 'scheduleGenerator.html',
                          {'reservedTimes': rt, 'possibleCourses': pc, 'error': error, 'course_count': course_count})

        # Loops through each section and period in the two lists
        for section in possible_sections:
            for period in possible_periods:
                if period in section.periods.all():  # If that possible period is in the possible section
                    # Finds the dictionary value corresponding to the section.id key.
                    # If there is not a key/value pair it creates it adds the period.id to the list
                    # If there is a k/v pair it just adds the period.id to the list.
                    course_sections[section.id] = course_sections.get(section.id, []) + [period.id]

        # Finds all the combinations of the lists passed in.
        def all_combinations(lst):
            # Chain links together the keys passed in through the dictionary.
            # Combinations gets all the possible key combinations
            return chain(*[combinations(lst, i + 1) for i in range(len(lst))])

        # Loops over all combinations of keys in the dictionary
        for comb in all_combinations(course_sections):  # comb is a list of section id
            # Loops over all combinations of values corresponding to the keys in comb list
            for prod in product(*(course_sections[k] for k in comb)):  # prod is a list of period id corresponding to section id
                use = dict(zip(comb, prod))  # Creates a dictionary relating the section id(s) to the period id(s)
                # Checks to see if the length of that dictionary is equal to the number of classes chosen by the user
                if len(use) == course_count:
                    # If it is it adds it to the list of dictionaries
                    # We only want the possible schedules that contain all the courses chosen by the user
                    permutations_dicts.append(use)

        # Used to compare dictionaries in the list and manipulate them
        for i in range(len(permutations_dicts)):  # i is the location in the list of dictionaries
            # We need to compare every k/v pair in each dictionary to find the repeated courses and period overlaps
            temp_dictionary = permutations_dicts[i]  # First temporary dictionary used for comparison to keep the original data safe
            temp_dictionary2 = permutations_dicts[i]  # Second temporary dictionary used for comparison to keep the original data safe
            # Looping over each key/value pair in both temporary dictionaries for comparison
            for k, v in temp_dictionary.items():
                for k2, v2 in temp_dictionary2.items():
                    if k == k2:  # We don't want to compare the section.ids that match because then all items will be removed from the
                        continue
                    else:
                        # Gets the actual objects associated with the ids
                        per1 = Period.objects.get(id=v)
                        per2 = Period.objects.get(id=v2)
                        sec1 = Section.objects.get(id=k)
                        sec2 = Section.objects.get(id=k2)
                        # Checks to see if there are sections with the same corresponding Course
                        if sec1.course.course_Title == sec2.course.course_Title:
                            items_to_remove.add(i)  # Adds the index of the dictionary to the set
                        # Checks to to see if the periods meet on the same day by comparing strings
                        if per1.meeting_day in per2.meeting_day or per2.meeting_day in per1.meeting_day:
                            # If they are on the same day this checks to see if times overlap
                            if per1.start_Time <= per2.start_Time and per2.end_Time <= per1.end_Time:
                                items_to_remove.add(i)
                                break
                            elif per2.start_Time <= per1.start_Time and per1.end_Time <= per2.end_Time:
                                items_to_remove.add(i)
                                break
                            elif per1.start_Time <= per2.start_Time <= per1.end_Time or per1.start_Time <= per2.end_Time <= per1.end_Time:
                                items_to_remove.add(i)
                                break

        # Adds the items in the dictionary of permutations to the schedule list if that dictionaries index is not in the items_to_remove set
        for i in range(len(permutations_dicts)):
            if i not in items_to_remove:
                schedules.append(permutations_dicts[i])

        # Loops through the list of schedules
        for i in range(len(schedules)):
            # Creates an instance of a schedule option for the user
            schedule_option = ScheduleOption.objects.create(user=current_user)
            # Loops through each kev/value pair in the dictionary at index i in the list of dictionaries
            for k, v in schedules[i].items():
                # Creates an instance of a pairing of Section and Period associated with a user
                scheduled_course = ScheduledCourses.objects.create(section_id=k, period_id=v, groupNumber=i)
                scheduled_course.save()
                # Adds that pairing to the Schedule option object
                schedule_option.scheduled_Courses.add(scheduled_course)
                # Saves the schedule option object
                schedule_option.save()

        # QuerySet to find the schedule options associated with a user
        schedule_options = ScheduleOption.objects.filter(user=current_user)

        if schedule_options.count() == 0:
            error = "There are no possible Schedules to be generated. Please choose a different set of Possible Schedules"
            return render(request, 'scheduleGenerator.html',
                          {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options,
                           'course_count': course_count, 'error': error})
        return render(request, 'scheduleGenerator.html',
                      {'reservedTimes': rt, 'possibleCourses': pc, 'schedule_Options': schedule_options, 'course_count': course_count})


@login_required  # Requires user to be logged in
# Function used to save a Schedule option
def saveSchedule(request, pk):
    if request.method == 'POST':
        # Grabs the requested schedule option
        schedule_option = ScheduleOption.objects.get(pk=pk)
        # Creates a new schedule object associated with the user
        saved_schedule = Schedule.objects.create(user=request.user)
        # Adds each scheduled course in the schedule option to the saved schedule
        for course in schedule_option.scheduled_Courses.all():
            saved_schedule.savedScheduledCourse.add(course)
        # Saves the saved schedule
        saved_schedule.save()
        messages.success(request, 'Schedule successfully saved.')
        return redirect('scheduleGenerator')


@login_required  # Requires user to be logged in
# Function used to retrieve and render the saved Schedule objects
def savedSchedules(request):
    try:  # Tries to find the Schedule objects associated with the user
        saved_schedules = Schedule.objects.filter(user=request.user)
    except ObjectDoesNotExist:
        saved_schedules = None
    # Returns the objects
    if request.method == 'GET':
        return render(request, 'savedSchedules.html', {'saved_schedules': saved_schedules})


@login_required  # Requires user to be logged in
# Function used to delete a saved Schedule object
def delSchedules(request, pk):
    # Creates an instance of the Schedule object with matching primary key
    schedule = Schedule.objects.get(pk=pk)
    if request.method == 'POST':
        # Deletes the Schedule object
        schedule.delete()
        return redirect('savedSchedules')

