from django.urls import path

from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('new/', views.group_create, name='group_create'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('<int:pk>/members/add/', views.add_member, name='add_member'),
]
