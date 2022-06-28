from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login as AuthLogin
from django.contrib import messages
from django.views import View
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from gp_admins.models import AccessLevel
from gp_admins.forms import LocalLoginForm
from gp_admins import api


def redirect_to_index_page(accesslevels):
    ''' Redirect to an index page given roles '''
    if 'Admin' in accesslevels or 'Manager' in accesslevels:
        return '/adm/home/'
    return '/stu/home/'


@require_http_methods(['GET'])
def login(request):
    ''' Login page '''
    if request.user.is_authenticated and 'loggedin_user' in request.session.keys():
        accesslevels = request.session['loggedin_user']['accesslevels']
        redirect_to = redirect_to_index_page(accesslevels)
        return HttpResponseRedirect(redirect_to)

    return render(request, 'accounts/login.html', {})


@method_decorator([never_cache], name='dispatch')
class LocalLoginView(View):
    ''' Local Login View '''

    form_class = LocalLoginForm

    @method_decorator(require_GET)
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and 'loggedin_user' in request.session.keys():
            accesslevels = request.session['loggedin_user']['accesslevels']
            redirect_to = redirect_to_index_page(accesslevels)
            return HttpResponseRedirect(redirect_to)

        return render(request, 'accounts/local_login.html', {
            'form': self.form_class()
        })

    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                AuthLogin(request, user)

                accesslevels = api.get_user_accesslevels(user)
                if len(accesslevels) == 0:
                    messages.error(request, 'An error occurred. Users must have at least one access level.')
                else:
                    request.session['loggedin_user'] = {
                        'id': user.id,
                        'username': user.username,
                        'accesslevels': accesslevels
                    }
                    redirect_to = redirect_to_index_page(accesslevels)
                    return HttpResponseRedirect(redirect_to)
            else:
                messages.error(request, 'An error occurred. Please check your username and password, then try again.')
        else:
            messages.error(request, 'An error occurred. Form is invalid. Please check your inputs.')

        return redirect('accounts:local_login')
