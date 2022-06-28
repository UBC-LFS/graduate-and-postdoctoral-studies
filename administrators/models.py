from django.db import models

from django.contrib.auth.models import User


class Term(models.Model):
    ''' Create a Term model '''
    code = models.CharField(max_length=20, unique=True)


class Session(models.Model):
    ''' Create a Session model '''

    year = models.CharField(max_length=4)
    term = models.ForeignKey(Term, on_delete=models.DO_NOTHING)


class CourseCode(models.Model):
    ''' Create a CourseCode model '''
    name = models.CharField(max_length=5, unique=True)


class CourseNumber(models.Model):
    ''' Create a CourseNumber model '''
    name = models.CharField(max_length=5, unique=True)


class CourseSection(models.Model):
    ''' Create a CourseSection model '''
    name = models.CharField(max_length=12, unique=True)


class Course(models.Model):
    ''' Create a Course model '''
    code = models.ForeignKey(CourseCode, on_delete=models.DO_NOTHING)
    number = models.ForeignKey(CourseNumber, on_delete=models.DO_NOTHING)
    section = models.ForeignKey(CourseSection, on_delete=models.DO_NOTHING)


class Job(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Classification(models.Model):
    year = models.CharField(max_length=10)
    name = models.CharField(max_length=10)
    wage = models.FloatField()


class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    classification = models.ForeignKey(Classification, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_declined_reassigned = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)


class ApplicationStatus(models.Model):
    '''
    Application Status

    # Updates
    Cancelled = Terminated
    '''
    NONE = '0'
    SELECTED = '1'
    OFFERED = '2'
    ACCEPTED = '3'
    DECLINED = '4'
    CANCELLED = '5'
    ASSSIGNED_CHOICES = [(NONE, 'None'), (SELECTED, 'Selected'), (OFFERED, 'Offered'), (ACCEPTED, 'Accepted'), (DECLINED, 'Declined'), (CANCELLED, 'Cancelled')]

    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    assigned = models.CharField(max_length=1, choices=ASSSIGNED_CHOICES, default=NONE)
    parent_id = models.CharField(max_length=256, null=True, blank=True)
