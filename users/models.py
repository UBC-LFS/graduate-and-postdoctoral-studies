from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User


def NumericalValueValidator(value):
    if value.isnumeric() == False:
        raise ValidationError(
            _('This field must be numerical value only.'), params={'value': value}, code='numerical_value'
        )


class Status(models.Model):
    name = models.CharField(max_length=256, unique=True)


class Program(models.Model):
    name = models.CharField(max_length=256, unique=True)


class Degree(models.Model):
    name = models.CharField(max_length=256, unique=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_number = models.CharField(
            max_length=8,
            unique=True,
            null=True,
            blank=True,
            validators=[
                NumericalValueValidator,
                MinLengthValidator(8),
                MaxLengthValidator(8)
            ]
        )

    status = models.ForeignKey(Status, on_delete=models.DO_NOTHING, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.DO_NOTHING, null=True, blank=True)
    program_others = models.TextField(null=True, blank=True)
    degrees = models.ManyToManyField(Degree)

    graduation_date = models.DateField(null=True, blank=True)
