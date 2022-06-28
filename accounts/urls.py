from django.conf import settings
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login')
]

if settings.LOCAL_LOGIN:
    urlpatterns += [
        path('local-login/', views.LocalLoginView.as_view(), name='local_login')
    ]
