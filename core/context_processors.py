def user_accesslevels(request):
    user_accesslevels = None
    if request.user.is_authenticated and 'loggedin_user' in request.session.keys():
        user_accesslevels = request.session['loggedin_user']['accesslevels']

    return {
        'user_accesslevels': user_accesslevels
    }
