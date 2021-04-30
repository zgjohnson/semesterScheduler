from django.contrib import admin
from catalog import models
from django.core.exceptions import ValidationError
from django import forms
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Course, Section, Period


# Modifies the Period Form in the Admin site
class PeriodAdminForm(forms.ModelForm):
    class Meta:
        model = models.Period
        fields = ['start_Time', 'end_Time', 'meeting_day']

    def clean(self):
        # Checks to see if time input is in increments of 5
        if self.cleaned_data['start_Time'].minute % 5 != 0 or self.cleaned_data['end_Time'].minute % 5 != 0:
            raise ValidationError("Please input a minute in increments of 5")
        return super().clean()


# CSV Import for Course
class CourseResource(resources.ModelResource):
    class Meta:
        model = Course


class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource


# CSV Import for Section

class SectionResource(resources.ModelResource):
    course = fields.Field(
        column_name='course',
        attribute='course',
        widget=ForeignKeyWidget(Course, 'id')
    )

    class Meta:
        model = Section
        fields = ('id', 'section_ID', 'instructor', 'course', 'periods')


class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource


# CSV Import for Period
class PeriodResource(resources.ModelResource):
    class Meta:
        model = Period


class PeriodAdmin(ImportExportModelAdmin):
    resource_class = PeriodResource
    form = PeriodAdminForm
    list_display = ("id", "start_Time", "end_Time", "meeting_day")

    def save_model(self, request, obj, form, change):
        obj.save()


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Section, SectionAdmin)
admin.site.register(models.Period, PeriodAdmin)
admin.site.register(models.DesignatedCourses)
admin.site.register(models.ReservedTime)
admin.site.register(models.ScheduleOption)
admin.site.register(models.ScheduledCourses)
admin.site.register(models.Schedule)

