from django.urls import path

from . import views

urlpatterns = [
    path('', views.handle_info, name='handle channels info'),
    path('<int:ch>/', views.handle_single_info, name='handle single channel info'),
]
