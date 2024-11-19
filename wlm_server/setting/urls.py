from django.urls import path

from . import views

urlpatterns = [
    path('<int:ch>/', views.handle_info, name='handle channel setting'),
]
