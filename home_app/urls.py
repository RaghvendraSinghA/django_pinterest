from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    # views.home is a function from home_app views.py
    ]
