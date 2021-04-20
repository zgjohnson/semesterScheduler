from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Course(models.Model):
    department_ID = models.CharField(max_length=4)
    course_Number = models.CharField(max_length=10)
    course_Title = models.CharField(max_length=255)

    def __str__(self):
        return self.course_Title


class Period(models.Model):
    start_Time = models.TimeField()
    end_Time = models.TimeField()

    MONDAY = 'M'
    TUESDAY = 'T'
    WEDNESDAY = 'W'
    THURSDAY = 'R'
    FRIDAY = 'F'
    MONWED = 'MW'
    MONWEDFRI = 'MWF'
    TUETHU = 'TR'
    MONTUEWEDTHUFRI = 'MTWRF'

    MEETING_DAY_CHOICES = [
        (MONDAY, 'M'),
        (TUESDAY, 'T'),
        (WEDNESDAY, 'W'),
        (THURSDAY, 'R'),
        (FRIDAY, 'F'),
        (MONWED, 'MW'),
        (MONWEDFRI, 'MWF'),
        (TUETHU, 'TR'),
        (MONTUEWEDTHUFRI, 'MTWRF')
    ]
    meeting_day = models.CharField(
        max_length=10,
        choices=MEETING_DAY_CHOICES,
    )

    def __str__(self):
        return str(self.meeting_day) + " " + str(self.start_Time) + "-" + str(self.end_Time)


class Section(models.Model):
    section_ID = models.CharField(max_length=20)
    instructor = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    periods = models.ManyToManyField(Period)

    def __str__(self):
        return self.course.course_Title + " " + self.section_ID


class DesignatedCourses(models.Model):
    designated_courses = models.ManyToManyField(Course)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username) + " Designated Courses"


class ReservedTime(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_Time = models.TimeField()
    end_Time = models.TimeField()
    description = models.CharField(max_length=150)

    MONDAY = 'M'
    TUESDAY = 'T'
    WEDNESDAY = 'W'
    THURSDAY = 'R'
    FRIDAY = 'F'

    DAY_CHOICES = [
        (MONDAY, 'M'),
        (TUESDAY, 'T'),
        (WEDNESDAY, 'W'),
        (THURSDAY, 'R'),
        (FRIDAY, 'F'),
    ]

    reserved_Day = models.CharField(max_length=10, choices=DAY_CHOICES, default='')

    def __str__(self):
        return self.description


class ScheduledCourses(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)

    groupNumber = models.IntegerField(default=0)


class ScheduleOption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scheduled_Courses = models.ManyToManyField(ScheduledCourses)


class Schedule(models.Model):
    savedScheduledCourse = models.ManyToManyField(ScheduledCourses)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user + "Schedule"
