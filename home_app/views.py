from django.shortcuts import render
from pin_app.models import Pin


# @login_required
def home(request):
    pins = Pin.objects.all()

    return render(request, "home/home.html", {"pins": pins})

