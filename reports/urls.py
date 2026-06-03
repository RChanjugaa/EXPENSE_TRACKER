from django.urls import path

from . import views

urlpatterns = [
    path('monthly/', views.monthly_report, name='monthly_report'),
    path('groups/', views.group_summary, name='group_summary'),
]
