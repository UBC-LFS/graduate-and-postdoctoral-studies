from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from urllib.parse import urlparse
from django.urls import resolve
from django.http import Http404
from django.contrib import messages

from gp_admins import api


def superadmin_access_only(view_func):
    ''' Only superadmins can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and request.user.is_superuser and 'Superadmin' in request.session['loggedin_user']['accesslevels']:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def admin_access_only(view_func):
    ''' Only admins can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and ('Superadmin' in request.session['loggedin_user']['accesslevels'] or 'Admin' in request.session['loggedin_user']['accesslevels']):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def supervisor_access_only(view_func):
    ''' Only supervisors can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and 'Supervisor' in request.session['loggedin_user']['accesslevels']:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def student_access_only(view_func):
    ''' Only students can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and 'Student' in request.session['loggedin_user']['accesslevels']:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def active_user_allowed(view_func):
    ''' Active users can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap
