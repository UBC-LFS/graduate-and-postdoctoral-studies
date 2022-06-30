from django.urls import path, include
from . import views

app_name = 'gp_admins'

urlpatterns = [
    path('home/', views.index, name='index'),
    path('applications/accepted/', views.get_accepted_apps, name='get_accepted_apps'),

    # TA Award Forms

    # Admin Menu
    path('admin-menu/users/', views.UsersView.as_view(), name='get_users'),
    path('api/users/<str:username>/edit/', views.EditUserView.as_view(), name='edit_user'),
    # path('api/users/delete/', views.delete_user, name='delete_user'),

    path('admin-menu/program-groups/', views.ProgramGroupView.as_view(), name='get_programgroups'),
    path('api/program-groups/delete/', views.delete_programgroup, name='delete_programgroup'),
    path('api/program-groups/<int:pg_id>/edit/', views.edit_programgroup, name='edit_programgroup'),

    path('admin-menu/users/access-levels/', views.AccessLevelsView.as_view(), name='get_accesslevels'),
    path('api/access-levels/delete/', views.delete_accesslevel, name='delete_accesslevel'),
    path('api/access-levels/<int:al_id>/edit/', views.edit_accesslevel, name='edit_accesslevel'),
]
