from django import forms
from django.forms import ModelForm
from registration.forms import RegistrationForm
from .models import Course, ReservedTime


class MyRegistrationForm(RegistrationForm):
    access_requested = forms.ChoiceField(choices=(('S', 'Student'), ('A', 'Admin'), ('R', 'Root')))


class DesignatedCoursesForm(forms.Form):
    choices = forms.ModelMultipleChoiceField(queryset=Course.objects.all(),
                                             widget=forms.CheckboxSelectMultiple)


class ReservedTimeForm(forms.ModelForm):

    class Meta:
        model = ReservedTime
        fields = ['description', 'start_Time', 'end_Time']
        widgets = {'start_Time': forms.TimeInput(attrs={'type': 'time'}),
                   'end_Time': forms.TimeInput(attrs={'type': 'time'})}

