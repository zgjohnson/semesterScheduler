from django.contrib import admin
from catalog import models
from django.core.exceptions import ValidationError
from django import forms


class PeriodAdminForm(forms.ModelForm):
    class Meta:
        model = models.Period
        fields = ['start_Time', 'end_Time', 'meeting_day']

    def clean(self):
        if self.cleaned_data['start_Time'].minute % 5 != 0 or self.cleaned_data['end_Time'].minute % 5 != 0:
            raise ValidationError("Please input a minute value divisible by 5")
        return super().clean()


class PeriodAdmin(admin.ModelAdmin):
    form = PeriodAdminForm
    list_display = ("id", "start_Time", "end_Time", "meeting_day")

    def save_model(self, request, obj, form, change):

        obj.save()



admin.site.register(models.Course)
admin.site.register(models.Section)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.DesignatedCourses)

#Periods time modification
#hide the actual start_Time and end_Time field
#create a new form field on the admin site for hour, minuet, and am/pm
    #for both start_Time and end_Time
#when displaying existing periods load actual start_Time
   #and end_Time from the database model

#create a clean method inside PeriodAdmin class
#create PeriodAdmin class - will take the three time fields, assemble it and store
    #it into the Periods database model

#create PeriodAdmin class
#clean method validates it is divisible by 5
#have message saying enter time in 5 minuet increments
#save_model function not clean