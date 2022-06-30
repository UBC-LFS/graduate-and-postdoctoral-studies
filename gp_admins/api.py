from django.db.models import Q
from django.http import Http404

from django.contrib.auth.models import User
from administrators.models import Application, ApplicationStatus
from .models import *
from .forms import *


def get_users():
    return User.objects.using('default').all().order_by('last_name', 'first_name')

def get_user_by_id(user_id):
    try:
        return User.objects.using('default').get(id=user_id)
    except User.DoesNotExist:
        raise Http404


def get_user_by_username(username):
    try:
        return User.objects.using('default').get(username=username)
    except User.DoesNotExist:
        raise Http404


def is_user_active(username):
    user = get_user_by_username(username)
    return user.is_active


def has_customfield_created(user):
    ''' Check an user has a custom field object '''
    try:
        return True
    except CustomField.DoesNotExist:
        return False


def user_exists(user_data):
    ''' Check user exists '''
    found_user = User.objects.using('default').filter(username=user_data['username'])
    if found_user.exists():
        user = found_user.first()
        if not has_customfield_created(user):
            if create_CustomField(user):
                return user
    return None


def create_user(user_data):
    ''' Create a user when receiving data from SAML '''
    user = User.objects.using('default').create(
        first_name = user_data['first_name'],
        last_name = user_data['last_name'],
        email = user_data['email'],
        username = user_data['username']
    )
    user.set_unusable_password()
    if user:
        if create_CustomField(user):
            return user
    return False


def create_customfield(user):
    ''' Create an user's member '''
    student_accesslevel = AccessLevel.objects.using('default').filter(name='Student').first()

    customfield_form = CustomFieldForm({ 'accesslevels': [student_accesslevel.id] })
    if custom_user_form.is_valid():
        customfield = CustomField.objects.using('default').create(user_id=user.id)
        customfield.accesslevels.add( *customfield_form.cleaned_data['accesslevels'] )
        return True
    return False


# Program Group

def get_programgroups():
    return ProgramGroup.objects.using('default').all()

def get_programgroup_by_id(pg_id):
    try:
        return ProgramGroup.objects.using('default').get(id=pg_id)
    except ProgramGroup.DoesNotExist:
        raise Http404


# Access Level

def get_user_accesslevels(user):
    ''' Add accesslevels into an user '''

    accesslevels = []
    for al in user.customfield.accesslevels.all():
        if al.name == AccessLevel.SUPERADMIN:
            accesslevels.append(AccessLevel.SUPERADMIN)
        elif al.name == AccessLevel.ADMIN:
            accesslevels.append(AccessLevel.ADMIN)
        elif al.name == AccessLevel.SUPERVISOR:
            accesslevels.append(AccessLevel.SUPERVISOR)
        elif al.name == AccessLevel.STUDENT:
            accesslevels.append(AccessLevel.STUDENT)
    return ', '.join(accesslevels)

def get_accesslevels():
    return AccessLevel.objects.using('default').all()

def get_accesslevel_by_id(al_id):
    try:
        return AccessLevel.objects.using('default').get(id=al_id)
    except AccessLevel.DoesNotExist:
        raise Http404


# Application

def add_app_info_into_application(app, list):
    ''' Add some information into an application given by list '''
    app.declined = None
    declined = app.applicationstatus_set.filter(assigned=ApplicationStatus.DECLINED)
    if declined.exists(): app.declined = declined.last()

    return app


def get_filtered_accepted_apps():
    ''' Get filtered accepted applications '''
    apps = Application.objects.using('ta_app_db').filter( Q(applicationstatus__assigned=ApplicationStatus.ACCEPTED) & Q(is_terminated=False) ).order_by('-id').distinct()
    excluded_apps = apps.filter( Q(is_declined_reassigned=True) & Q(applicationstatus__assigned=ApplicationStatus.DECLINED) )

    excluded_ids = []
    for app in excluded_apps:
        ret_app = add_app_info_into_application(app, ['declined'])
        if ret_app.declined.parent_id == None:
            excluded_ids.append(ret_app.id)

    return apps.exclude(id__in=excluded_ids)


# Helper function


def check_two_querysets_equal(qs1, qs2):
    ''' Helper funtion: To check whether two querysets are equal or not '''
    if len(qs1) != len(qs2):
        return False

    d = dict()
    for qs in qs1:
        item = qs.name.lower()
        if item in d.keys(): d[item] += 1
        else: d[item] = 1

    for qs in qs2:
        item = qs.name.lower()
        if item in d.keys(): d[item] += 1
        else: d[item] = 1

    for k, v in d.items():
        if v != 2: return False
    return True
