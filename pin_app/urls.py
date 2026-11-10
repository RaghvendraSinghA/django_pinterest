from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.create_pin, name="create_pin"),
    path("<int:pin_id>/", views.pin_detail, name="pin_detail"),
    path("pin/<int:pin_id>/delete/", views.delete_pin, name="delete_pin"),
    path("pin/<int:pin_id>/like/", views.like_pin, name="like_pin"),
    path("pin/<int:pin_id>/comment/", views.add_comment, name="add_comment"),
    
    path("pin/<int:pin_id>/comment/<int:comment_id>/reply/",
         views.add_reply,
        name="add_reply"),

    path("comment/<int:comment_id>/delete/",
          views.delete_comment, 
          name="delete_comment"
    ),

    path("user/<int:user_id>/follow/", views.follow_user, name="follow_user"),
    path("search/", views.search_pins, name="search_pins"),
    path(
        "comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment"
    ),
    path(
        "pin/<int:pin_id>/edit-title/",
        views.edit_pin_title,
        name="edit_pin_title"
    ),
    path(
        "pin/<int:pin_id>/edit/",
        views.edit_pin,
        name="edit_pin"
    )
]
