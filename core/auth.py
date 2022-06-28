from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from urllib.parse import urlparse
from django.urls import resolve
from django.http import Http404
from django.contrib import messages

from ta_award import api


def admin_access_only(view_func):
    ''' Only admins can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and request.user.is_superuser and 'Admin' in request.session['loggedin_user']['accesslevels']:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap


def admin_manager_access_only(view_func):
    ''' Only admins and managers can access '''
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active and ('Admin' in request.session['loggedin_user']['accesslevels'] or 'Manager' in request.session['loggedin_user']['accesslevels']):
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
