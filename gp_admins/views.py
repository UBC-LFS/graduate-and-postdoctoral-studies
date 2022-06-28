from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from .models import AccessLevel
from .forms import AccessLevelForm, UserForm, CustomFieldEditForm
from core.auth import admin_access_only, admin_manager_access_only, active_user_allowed
from gp_admins import api


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['GET'])
@admin_manager_access_only
def index(request):
    return render(request, 'gp_admins/index.html', {
        'apps': api.get_filtered_accepted_apps(),
        'users': User.objects.using('default').all()
    })


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['GET'])
@admin_manager_access_only
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
        user_list = User.objects.using('default').all().order_by('last_name', 'first_name')

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

        return render(request, 'gp_admins/get_users.html', {
            'users': users,
            'total_users': len(user_list),
            'form': self.form_class()
        })


@method_decorator([never_cache, login_required, admin_access_only], name='dispatch')
class EditUserView(View):
    ''' Users View '''
    user_form_class = UserForm
    custom_user_edit_form_class = CustomFieldEditForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        user = api.get_user_by_username(kwargs['username'])

        # To check whether a member object has been created or not
        if not api.has_custom_user_created(user):
            user.customfield = CustomField.objects.using('default').create(user_id=user.id)

        return render(request, 'gp_admins/edit_user.html', {
            'user': user,
            'user_form': self.user_form_class(data=None, instance=user),
            'custom_user_edit_form': self.custom_user_edit_form_class(data=None, instance=user.customfield)
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        user = api.get_user_by_id(request.POST['user'])

        user_form = self.user_form_class(request.POST, instance=user)
        custom_user_edit_form = self.custom_user_edit_form_class(request.POST, instance=user.customfield)

        if user_form.is_valid() and custom_user_edit_form.is_valid():
            if user_form.save():

                # Update access levels of this user
                old_accesslevels = user.customfield.accesslevels.all()
                user.customfield.accesslevels.remove( *old_accesslevels )
                new_accesslevels = list(custom_user_edit_form.cleaned_data.get('accesslevels'))
                user.customfield.accesslevels.add( *new_accesslevels )

                messages.success(request, 'Success! The information of {0} (CWL: {1}) has been updated'.format(user.get_full_name(), user.username))
            else:
                messages.error(request, 'An error occurred while updating an User Form.')
        else:
            errors = []
            user_errors = user_form.errors.get_json_data()
            custom_user_errors = custom_user_edit_form.errors.get_json_data()

            if user_errors: errors.append(user_errors)
            if custom_user_errors: errors.append(custom_user_errors)

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


#--- Access Levels

@method_decorator([never_cache, login_required, admin_access_only], name='dispatch')
class AccessLevelsView(View):
    ''' Access Levels View '''

    form_class = AccessLevelForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        return render(request, 'gp_admins/get_accesslevels.html', {
            'accesslevels': AccessLevel.objects.using('default').all(),
            'form': self.form_class()
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            accesslevel = form.save()
            if accesslevel:
                messages.success(request, 'Success! {0} has been created'.format(accesslevel.name))
            else:
                messages.error(request, 'An error occurred while saving data.')
        else:
            #errors = form.errors.get_json_data()
            messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))

        return redirect('gp_admins:get_accesslevels')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@admin_access_only
def edit_accesslevel(request, accesslevel_id):
    ''' Edit an access level '''
    form = AccessLevelForm(request.POST, instance=api.get_accesslevel_by_id(accesslevel_id))
    if form.is_valid():
        ac = form.save()
        if ac:
            messages.success(request, 'Success! {0} has been updated'.format(ac.name))
        else:
            messages.error(request, 'An error occurred while updating data.')
    else:
        #errors = form.errors.get_json_data()
        messages.error(request, 'An error occurred. Form is invalid. {0}'.format(form.errors))
    return redirect('gp_admins:get_accesslevels')


@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['POST'])
@admin_access_only
def delete_accesslevel(request):
    ''' Delete an access level '''
    ac = api.get_accesslevel_by_id( request.POST.get('accesslevel') )
    ac.delete()
    if ac:
        messages.success(request, 'Success! {0} has been deleted'.format(ac.name))
    else:
        messages.error(request, 'An error occurred.')
    return redirect('gp_admins:get_accesslevels')
