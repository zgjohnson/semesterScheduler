from django import forms
from registration.forms import RegistrationForm


class MyRegistrationForm(RegistrationForm):
    access_requested = forms.ChoiceField(choices=(('S', 'Student'), ('A', 'Admin'), ('R', 'Root')))
