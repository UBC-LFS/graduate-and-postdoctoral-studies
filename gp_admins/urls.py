from django.urls import path, include
from . import views

app_name = 'gp_admins'

urlpatterns = [
    path('home/', views.index, name='index'),
    path('applications/accepted/', views.get_accepted_apps, name='get_accepted_apps'),

    path('users/', views.UsersView.as_view(), name='get_users'),
    # path('api/users/delete/', views.delete_user, name='delete_user'),
    path('api/users/<str:username>/edit/', views.EditUserView.as_view(), name='edit_user'),

    path('users/access-levels/', views.AccessLevelsView.as_view(), name='get_accesslevels'),
    path('api/members/access-levels/delete/', views.delete_accesslevel, name='delete_accesslevel'),
    path('api/members/access-levels/<int:accesslevel_id>/edit/', views.edit_accesslevel, name='edit_accesslevel')
]
