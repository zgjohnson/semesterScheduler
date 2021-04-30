from django import forms
from registration.forms import RegistrationForm
from .models import Course, ReservedTime


# Extends the Registration Form from Django Registration-Redux
class MyRegistrationForm(RegistrationForm):
    # Allows user to choose a privilege setting
    access_requested = forms.ChoiceField(choices=(('S', 'Student'), ('A', 'Admin'), ('R', 'Root')))


# Form used on Possible Courses page
class DesignatedCoursesForm(forms.Form):
    # Queries the database for all Course objects and lists them with the option to check
    choices = forms.ModelMultipleChoiceField(queryset=Course.objects.all(),
                                             widget=forms.CheckboxSelectMultiple)


# Form used to enter a Reserved Time
class ReservedTimeForm(forms.ModelForm):

    class Meta:
        # Models data after the Reserved Time data model
        model = ReservedTime
        # Lists the fields for the model
        fields = ['description', 'reserved_Day', 'start_Time', 'end_Time']
        # Changes the way you can input the time to make it more user friendly
        widgets = {'start_Time': forms.TimeInput(attrs={'type': 'time'}),
                   'end_Time': forms.TimeInput(attrs={'type': 'time'})}

