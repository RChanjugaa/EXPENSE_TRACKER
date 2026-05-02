from django.urls import path

from . import views

urlpatterns = [
    path('groups/<int:group_pk>/new/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/members/add/', views.add_expense_participant, name='add_expense_participant'),
    path('<int:pk>/invite/', views.invite_to_expense, name='invite_to_expense'),
    path('invitations/<str:token>/accept/', views.accept_expense_invitation, name='accept_expense_invitation'),
]
