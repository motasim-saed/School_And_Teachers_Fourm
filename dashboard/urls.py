# في dashboard/urls.py

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('schools/', views.view_schools_list, name='schools_list'),
    path('teachers/', views.view_teachers_list, name='teachers_list'),
]
