from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    
    path("pin/<int:pin_id>/", views.pin_detail, name="pin_detail"),

    path("pin/<int:pin_id>/delete/", views.delete_pin, name="delete_pin"),

    path(
    "pin/<int:pin_id>/like/",
    views.like_pin,
    name="like_pin"
    ),

    path(
    "pin/<int:pin_id>/comment/",
    views.add_comment,
    name="add_comment"
    ),

    path(
    "pin/<int:pin_id>/comment/<int:comment_id>/reply/",
    views.add_reply,
    name="add_reply"
    ),

    path(
    "comment/<int:comment_id>/delete/",
    views.delete_comment,
    name="delete_comment"
    ),
]