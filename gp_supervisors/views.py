from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from core.auth import *

@login_required(login_url=settings.LOGIN_URL)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_http_methods(['GET'])
@supervisor_access_only
def index(request):
    return render(request, 'gp_supervisors/index.html', {
        'programgroups': request.user.customfield.programgroups.all()
    })
