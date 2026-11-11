from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Board
from pin_app.models import Pin
from .forms import BoardForm
import logging


logger = logging.getLogger(__name__)


@login_required
def create_board_view(request):
    if request.method == "POST":
        form = BoardForm(request.POST)

        if form.is_valid():
            board = form.save(commit=False)
            board.user = request.user

            try:
                board.save()
            except Exception:
                logger.exception(
                    "Failed to create Board for user %s",
                    request.user.id
                )
                raise

            return redirect("profile", username=request.user.username)

    else:
        form = BoardForm()

    return render(
        request,
        "board/create_board.html",
        {"form": form},
    )


@login_required
def board_detail_view(request, board_id):
    board = get_object_or_404(
        Board.objects.prefetch_related("pins"),
        id=board_id,
    )

    return render(
        request,
        "board/board_detail.html",
        {
            "board": board,
            "pins": board.pins.all(),
        },
    )


@login_required
@require_POST
def save_pin_to_board_view(request, pin_id):
    pin = get_object_or_404(Pin, id=pin_id)

    board = get_object_or_404(
        Board,
        id=request.POST.get("board_id"),
        user=request.user,
    )

    try:
        board.pins.add(pin)

    except Exception:
        logger.exception(
            "Failed to save Pin %s to Board %s",
            pin.id,
            board.id
        )
        raise

    return JsonResponse({"success": True})


@login_required
@require_POST
def delete_board_view(request, board_id):
    board = get_object_or_404(
        Board,
        id=board_id,
        user=request.user,
    )

    username = request.user.username

    try:
        board.delete()
    except Exception:
        logger.exception(
            "Failed to delete Board %s",
            board.id
        )
        raise

    return redirect("profile", username=username)


@login_required
@require_POST
def remove_pin_from_board_view(request, board_id, pin_id):
    board = get_object_or_404(
        Board,
        id=board_id,
        user=request.user,
    )

    pin = get_object_or_404(
        Pin,
        id=pin_id,
    )

    try:
        board.pins.remove(pin)

    except Exception:
        logger.exception(
            "Failed to remove Pin %s from Board %s",
            pin.id,
            board.id
        )
        raise

    return redirect("board_detail", board_id=board.id)


@login_required
@require_POST
def edit_board_name(request, board_id):
    board = get_object_or_404(
        Board,
        id=board_id,
        user=request.user
    )

    name = request.POST.get("name", "").strip()

    if not name:
        return JsonResponse(
            {"error": "Board name cannot be empty"},
            status=400
        )

    try:
        board.name = name
        board.save(update_fields=["name"])

    except Exception:
        logger.exception(
            "Failed to rename Board %s",
            board.id
        )
        raise

    return JsonResponse({
        "success": True,
        "name": board.name
    })
