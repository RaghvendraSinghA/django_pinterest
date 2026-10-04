from django.shortcuts import render, redirect
from .forms import PinForm


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