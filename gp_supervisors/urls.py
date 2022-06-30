from django.urls import path, include
from . import views

app_name = 'gp_supervisors'

urlpatterns = [
    path('home/', views.index, name='index'), 
]