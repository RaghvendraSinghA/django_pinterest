from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_pin, name="create_pin"),
    path("boards/create/", views.create_board_view, name="create_board"),
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
]
