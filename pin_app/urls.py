from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_pin, name="create_pin"),
]