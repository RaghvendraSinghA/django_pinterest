from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Board
from pin_app.models import Pin
from .forms import BoardForm

# Create your views here.



@login_required
def create_board_view(request):
    if request.method == "POST":
        form = BoardForm(request.POST)

        if form.is_valid():
            board = form.save(commit=False)
            board.user = request.user
            board.save()

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

    board.pins.add(pin)

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

    board.delete()

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

    board.pins.remove(pin)

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

    board.name = name
    board.save(update_fields=["name"])

    return JsonResponse({
        "success": True,
        "name": board.name
    })