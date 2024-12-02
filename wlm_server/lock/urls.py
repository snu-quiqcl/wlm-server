from django.urls import path

from . import views

urlpatterns = [
    path('<int:ch>/try/', views.try_lock, name='try to acquire lock'),
    path('<int:ch>/release/', views.release_lock, name='release lock'),
]
