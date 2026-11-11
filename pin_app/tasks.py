from celery import shared_task
from django.core.files import File
from pin_app.models import Pin
import cloudinary.uploader
from pinterest_config.elasticsearch import es
from elasticsearch import NotFoundError


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



@shared_task
def index_pin(pin_id):
    try:
        pin = Pin.objects.get(id=pin_id)

        es.index(
            index="pins",
            id=pin.id,
            document={
                "id": pin.id,
                "title": pin.title,
                "description": pin.description
            }
        )

        return f"Pin {pin_id} indexed successfully"

    except Pin.DoesNotExist:
        return f"Pin {pin_id} not found"



@shared_task
def delete_pin_from_elasticsearch(pin_id):
    try:
        es.delete(
            index="pins",
            id=pin_id
        )

        print(f"Pin {pin_id} deleted from Elasticsearch successfully")

        return f"Pin {pin_id} deleted successfully"

    except NotFoundError:
        print(f"Pin {pin_id} was not found in Elasticsearch")

        return f"Pin {pin_id} not found"