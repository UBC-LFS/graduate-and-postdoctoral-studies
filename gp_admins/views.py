from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User
from .models import *
from .forms import *
from core.auth import *
from gp_admins import api


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['GET'])
@admin_access_only
def index(request):
    return render(request, 'gp_admins/index.html', {
        'apps': api.get_filtered_accepted_apps(),
        'users': User.objects.using('default').all()
    })


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['GET'])
@admin_access_only
def get_accepted_apps(request):
    ''' Get a list of accepted applications '''

    app_list = api.get_filtered_accepted_apps()

    if bool( request.GET.get('year') ):
        app_list = app_list.filter(job__session__year__icontains=request.GET.get('year'))
    if bool( request.GET.get('first_name') ):
        app_list = app_list.filter(applicant__first_name__icontains=request.GET.get('first_name'))
    if bool( request.GET.get('last_name') ):
        app_list = app_list.filter(applicant__last_name__icontains=request.GET.get('last_name'))
    if bool( request.GET.get('cwl') ):
        app_list = app_list.filter(applicant__username__icontains=request.GET.get('cwl'))
    if bool( request.GET.get('student_number') ):
        app_list = app_list.filter(applicant__profile__student_number__icontains=request.GET.get('student_number'))

    page = request.GET.get('page', 1)
    paginator = Paginator(app_list, settings.PAGE_SIZE)

    try:
        apps = paginator.page(page)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)

    return render(request, 'gp_admins/get_accepted_apps.html', {
        'apps': apps,
        'total_apps': len(app_list)
    })


#--- Users

@method_decorator([never_cache, login_required, admin_access_only], name='dispatch')
class UsersView(View):
    ''' Users View '''

    form_class = AccessLevelForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        user_list = api.get_users()

        if bool( request.GET.get('first_name') ):
            user_list = user_list.filter(first_name__icontains=request.GET.get('first_name'))
        if bool( request.GET.get('last_name') ):
            user_list = user_list.filter(last_name__icontains=request.GET.get('last_name'))
        if bool( request.GET.get('cwl') ):
            user_list = user_list.filter(username__icontains=request.GET.get('cwl'))

        page = request.GET.get('page', 1)
        paginator = Paginator(user_list, settings.PAGE_SIZE)

        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return render(request, 'gp_admins/admin_menu/get_users.html', {
            'users': users,
            'total_users': len(user_list),
            'form': self.form_class()
        })


@method_decorator([never_cache, login_required, admin_access_only], name='dispatch')
class EditUserView(View):
    ''' Users View '''
    user_form_class = UserForm
    customfield_edit_form_class = CustomFieldEditForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        user = api.get_user_by_username(kwargs['username'])

        # To check whether a customfield object has been created or not
        if not api.has_customfield_created(user):
            user.customfield = CustomField.objects.using('default').create(user_id=user.id)

        return render(request, 'gp_admins/admin_menu/edit_user.html', {
            'user': user,
            'user_form': self.user_form_class(data=None, instance=user),
            'customfield_edit_form': self.customfield_edit_form_class(data=None, instance=user.customfield)
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        user = api.get_user_by_id(request.POST['user'])

        user_form = self.user_form_class(request.POST, instance=user)
        customfield_edit_form = self.customfield_edit_form_class(request.POST, instance=user.customfield)

        if user_form.is_valid() and customfield_edit_form.is_valid():
            if user_form.save():

                # Program Group
                old_programgroups = user.customfield.programgroups.all()
                if api.check_two_querysets_equal(old_programgroups, customfield_edit_form.cleaned_data.get('programgroups')) == False:
                    user.customfield.programgroups.remove( *old_programgroups ) # Remove current program groups
                    new_programgroups = list( customfield_edit_form.cleaned_data.get('programgroups') )
                    user.customfield.programgroups.add( *new_programgroups ) # Add new program groups

                # Access Level: To check wheter access levels of this user should be updated or not
                old_accesslevels = user.customfield.accesslevels.all()
                if api.check_two_querysets_equal(old_accesslevels, customfield_edit_form.cleaned_data.get('accesslevels')) == False:
                    user.customfield.accesslevels.remove( *old_accesslevels ) # Remove current access levels
                    new_accesslevels = list( customfield_edit_form.cleaned_data.get('accesslevels') )
                    user.customfield.accesslevels.add( *new_accesslevels ) # Add new access levels

                messages.success(request, 'Success! The user information of {0} has been updated.'.format(user.get_full_name()))
            else:
                messages.error(request, 'An error occurred while updating an User Form.')
        else:
            errors = []
            user_errors = user_form.errors.get_json_data()
            customfield_errors = customfield_edit_form.errors.get_json_data()

            if user_errors: errors.append(user_errors)
            if customfield_errors: errors.append(customfield_errors)

            messages.error(request, 'An error occurred while updating an User Form. {0}'.format( ' '.join(errors) ))

        return HttpResponseRedirect(request.POST.get('next'))

#
# # @login_required(login_url=settings.LOGIN_URL)
# # @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# # @require_http_methods(['POST'])
# # def delete_user(request):
# #     ''' Delete an user '''
# #
# #     user = api.get_user_by_id(request.POST['user'])
# #     full_name = user.get_full_name()
# #     print(user)
# #     user.delete()
# #
# #     print(User.objects.using('default').filter(id=user.id).exists())
# #     if User.objects.using('default').filter(id=user.id).exists():
# #         messages.error(request, 'Error! failed to delete this user')
# #     else:
# #         messages.success(request, 'Success! User {0} has been deleted'.format(full_name))
# #     return HttpResponseRedirect(request.POST.get('next'))



#--- Program Group

@method_decorator([never_cache, login_required, admin_access_only], name='dispatch')
class ProgramGroupView(View):
    ''' Program Group View '''

    form_class = ProgramGroupForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        return render(request, 'gp_admins/admin_menu/get_programgroups.html', {
            'programgroups': api.get_programgroups(),
            'form': self.form_class()
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            pg = form.save()
            if pg:
                messages.success(request, 'Success! Program Group - {0} - has been created'.format(pg.name))
            else:
                messages.error(request, 'An error occurred while saving data.')
        else:
            messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))

        return redirect('gp_admins:get_programgroups')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@admin_access_only
def edit_programgroup(request, pg_id):
    ''' Edit a program group '''
    form = ProgramGroupForm(request.POST, instance=api.get_programgroup_by_id(pg_id))
    if form.is_valid():
        pg = form.save()
        if pg:
            messages.success(request, 'Success! Program Group - {0} - has been updated'.format(pg.name))
        else:
            messages.error(request, 'An error occurred while updating data.')
    else:
        messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))
    return redirect('gp_admins:get_programgroups')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@admin_access_only
def delete_programgroup(request):
    ''' Delete a program group '''
    pg = api.get_programgroup_by_id( request.POST.get('programgroup') )
    pg.delete()
    if pg:
        messages.success(request, 'Success! Program Group - {0} - has been deleted'.format(pg.name))
    else:
        messages.error(request, 'An error occurred.')
    return redirect('gp_admins:get_programgroups')


#--- Access Levels

@method_decorator([never_cache, login_required, superadmin_access_only], name='dispatch')
class AccessLevelsView(View):
    ''' Access Levels View '''

    form_class = AccessLevelForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        return render(request, 'gp_admins/admin_menu/get_accesslevels.html', {
            'accesslevels': api.get_accesslevels(),
            'form': self.form_class()
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            al = form.save()
            if al:
                messages.success(request, 'Success! Access Level - {0} - has been created'.format(al.name))
            else:
                messages.error(request, 'An error occurred while saving data.')
        else:
            messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))

        return redirect('gp_admins:get_accesslevels')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@superadmin_access_only
def edit_accesslevel(request, al_id):
    ''' Edit an access level '''
    form = AccessLevelForm(request.POST, instance=api.get_accesslevel_by_id(al_id))
    if form.is_valid():
        al = form.save()
        if al:
            messages.success(request, 'Success! Access Level - {0} - has been updated'.format(al.name))
        else:
            messages.error(request, 'An error occurred while updating data.')
    else:
        messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))
    return redirect('gp_admins:get_accesslevels')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@superadmin_access_only
def delete_accesslevel(request):
    ''' Delete an access level '''
    al = api.get_accesslevel_by_id( request.POST.get('accesslevel') )
    al.delete()
    if al:
        messages.success(request, 'Success! Access Level - {0} - has been deleted'.format(al.name))
    else:
        messages.error(request, 'An error occurred.')
    return redirect('gp_admins:get_accesslevels')
