from django.contrib import admin
from catalog import models
from django.core.exceptions import ValidationError
from django import forms
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Course


class PeriodAdminForm(forms.ModelForm):
    class Meta:
        model = models.Period
        fields = ['start_Time', 'end_Time', 'meeting_day']

    def clean(self):
        if self.cleaned_data['start_Time'].minute % 5 != 0 or self.cleaned_data['end_Time'].minute % 5 != 0:
            raise ValidationError("Please input a minute in increments of 5")
        return super().clean()


class PeriodAdmin(admin.ModelAdmin):
    form = PeriodAdminForm
    list_display = ("id", "start_Time", "end_Time", "meeting_day")

    def save_model(self, request, obj, form, change):
        obj.save()


class CourseResource(resources.ModelResource):
    class Meta:
        model = Course
        exclude = ('id',)


class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Section)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.DesignatedCourses)
admin.site.register(models.ReservedTime)
admin.site.register(models.ScheduleOption)
admin.site.register(models.ScheduledCourses)
admin.site.register(models.Schedule)

# create PeriodAdmin class
# clean method validates it is divisible by 5
# have message saying enter time in 5 minuet increments
# save_model function not clean
