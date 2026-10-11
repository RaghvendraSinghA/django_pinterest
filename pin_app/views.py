from django.shortcuts import render, redirect, get_object_or_404
from .forms import PinForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import BoardForm
from .models import Board, Pin
from django.http import JsonResponse


@login_required
def create_pin(request):

    if request.method == "POST":
        form = PinForm(request.POST, request.FILES)

        if form.is_valid():
            pin = form.save(commit=False)
            pin.user = request.user
            pin.save()

            return redirect("home")

    else:
        form = PinForm()

    return render(request, "pin/create_pin.html", {"form": form})




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
        "pin/create_board.html",
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
        "pin/board_detail.html",
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