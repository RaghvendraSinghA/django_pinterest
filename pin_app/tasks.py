from celery import shared_task
from django.core.files import File
from django.core.files.storage import storages
from pin_app.models import Pin
import cloudinary.uploader


@shared_task
def add(x, y):
    return x + y


@shared_task
def upload_pin_image(pin_id):

    pin = Pin.objects.get(id=pin_id)

    if not pin.temp_image:
        return "No temporary image found"

    try:
        with pin.temp_image.open("rb") as image_file:
            pin.image.save(
                pin.temp_image.name.split("/")[-1],
                File(image_file),
                save=False,
            )

        pin.upload_status = "uploaded"
        pin.save(update_fields=["image", "upload_status"])

        delete_temp_pin_image.apply_async(
            args=[pin.id],
            countdown=300
        )

        return "Image uploaded successfully"

    except Exception:
        pin.upload_status = "failed"
        pin.save(update_fields=["upload_status"])
        raise



@shared_task
def delete_temp_pin_image(pin_id):
    try:
        pin = Pin.objects.get(id=pin_id)

        if pin.temp_image:
            pin.temp_image.delete(save=False)
            pin.temp_image = None
            pin.save(update_fields=["temp_image"])

        return "Temporary image deleted"

    except Pin.DoesNotExist:
        return "Pin not found"


import cloudinary.uploader
from celery import shared_task


@shared_task
def delete_pin_image(image_name):
    if image_name:
        result = cloudinary.uploader.destroy(image_name)
        return result