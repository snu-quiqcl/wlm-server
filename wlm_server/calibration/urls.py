from django.urls import path

from . import views

urlpatterns = [
    path('', views.calibrate, name='calibrate WLM'),
]
