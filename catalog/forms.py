from django import forms
from registration.forms import RegistrationForm
from .models import Course


class MyRegistrationForm(RegistrationForm):
    access_requested = forms.ChoiceField(choices=(('S', 'Student'), ('A', 'Admin'), ('R', 'Root')))


class DesignatedCoursesForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(queryset=Course.objects.all(),
                                             widget=forms.CheckboxSelectMultiple)


# textfield - description

#time range(start/end)
