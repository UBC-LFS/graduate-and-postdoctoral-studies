from django.db import models

from django.contrib.auth.models import User


class AccessLevel(models.Model):
    ADMIN = 'Admin'
    MANAGER = 'Manager'
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


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    accesslevels = models.ManyToManyField(AccessLevel)
