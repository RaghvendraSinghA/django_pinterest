from django.urls import path
from . import views

urlpatterns = [
    path("boards/create/",
          views.create_board_view,
          name="create_board"),
    path(
        "boards/<int:board_id>/",
        views.board_detail_view,
        name="board_detail",
    ),
    path(
        "<int:pin_id>/save/",
        views.save_pin_to_board_view,
        name="save_pin_to_board",
    ),
     path(
        "boards/<int:board_id>/delete/",
        views.delete_board_view,
        name="delete_board",
    ),
    path(
        "boards/<int:board_id>/pins/<int:pin_id>/remove/",
        views.remove_pin_from_board_view,
        name="remove_pin_from_board",
    ),
    path(
        "boards/<int:board_id>/edit/",
        views.edit_board_name,
        name="edit_board_name"
    ),
]