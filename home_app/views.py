
import logging

from django.shortcuts import render
from pin_app.models import Pin


logger = logging.getLogger(__name__)


def home(request):

    logger.debug(
        "User %s accessed the home page",
        getattr(request.user, "id", None)
    )

    try:
        pins = Pin.objects.all()
    except Exception:
        logger.exception("Failed to fetch Pins for home page")
        raise

    return render(
        request,
        "home/home.html",
        {"pins": pins}
    )
