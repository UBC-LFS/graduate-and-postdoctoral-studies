from django.shortcuts import render, redirect


def index(request):
    ''' App index page '''
    print('index')
    return redirect('accounts:login')


def bad_request(request, exception, template_name='400.html'):
    ''' Exception handlder for bad request '''
    print('bad_request')
    return render(request, 'core/400.html', {}, status=400)


def permission_denied(request, exception, template_name='403.html'):
    ''' Exception handlder for permission denied '''
    print('permission_denied')
    return render(request, 'core/403.html', {}, status=403)


def page_not_found(request, exception, template_name='404.html'):
    ''' Exception handlder for page not found '''
    print('page_not_found')
    return render(request, 'core/404.html', {}, status=404)


def internal_server_error(request, template_name='500.html'):
    ''' Exception handlder for page not found '''
    print('internal_server_error')
    return render(request, 'core/500.html', {}, status=500)
