from django.db import models


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
    MONTUEWEDTHUFRI = 'MWTWRF'

    MEETING_DAY_CHOICES = [
        (MONDAY, 'M'),
        (TUESDAY, 'T'),
        (WEDNESDAY, 'W'),
        (THURSDAY, 'R'),
        (FRIDAY, 'F'),
        (MONWED, 'MW'),
        (MONWEDFRI, 'MWF'),
        (TUETHU, 'TR'),
        (MONTUEWEDTHUFRI, 'MWTWRF')
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
        return self.section_ID

#class DesignatedCourses(models.Model):
    #Dictionary to hold the Courses the key being the Course ID and the value being the Course
    #I think this would be the best holder for our Course obects. We could also use a set
    #A set would not let any repeat which is good but it would also not keep them ordered.
    #I am not sure yet if they need to be ordered for what we need.
    #designated_Courses = {}
    #This model will need to reference a specific user so there needs to be a foreign key referencing a user.
