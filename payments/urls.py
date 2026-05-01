from django.urls import path

from . import views

urlpatterns = [
    path('', views.payment_history, name='payment_history'),
    path('<int:pk>/proof/', views.upload_proof, name='upload_proof'),
    path('<int:pk>/verify/', views.verify_payment, name='verify_payment'),
]
