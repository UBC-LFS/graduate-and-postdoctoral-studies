from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from django.contrib.auth.models import User


class AccessLevel(models.Model):
    SUPERADMIN = 'Superadmin'
    ADMIN = 'Admin'
    SUPERVISOR = 'Supervisor'
    STUDENT = 'Student'

    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(AccessLevel, self).save(*args, **kwargs)


def validate_name_caseinsensitive(name):
    if ProgramGroup.objects.filter(name__iexact=name).exists():
        raise ValidationError('This NAME already exists.')
    return name

class ProgramGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, validators=[validate_name_caseinsensitive])
    code = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ProgramGroup, self).save(*args, **kwargs)


class CustomField(models.Model):
    ''' Auth User Custom Field '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    programgroups = models.ManyToManyField(ProgramGroup)
    accesslevels = models.ManyToManyField(AccessLevel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
