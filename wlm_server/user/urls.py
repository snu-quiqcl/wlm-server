from django.urls import path

from . import views

urlpatterns = [
    path('signin/', views.sign_in, name='sign in'),
    path('signout/', views.sign_out, name='sign out'),
    path('me/', views.handle_info, name='handle my info'),
]
