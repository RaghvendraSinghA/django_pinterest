import logging
from celery import shared_task
from django.core.files import File
from pin_app.models import Pin
import cloudinary.uploader
from pinterest_config.elasticsearch import es
from elasticsearch import NotFoundError


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def upload_pin_image(self, pin_id):

    try:
        pin = Pin.objects.get(id=pin_id)

        if not pin.temp_image:
            return "No temporary image found"

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

    except Pin.DoesNotExist:
        return "Pin not found"

    except Exception as exc:

        logger.exception(
            "Image upload failed for Pin %s. Retry %s/%s",
            pin_id,
            self.request.retries,
            self.max_retries
        )

        if self.request.retries >= self.max_retries:
            try:
                pin = Pin.objects.get(id=pin_id)
                pin.upload_status = "failed"
                pin.save(update_fields=["upload_status"])
            except Exception:
                logger.exception(
                    "Could not update upload status for Pin %s",
                    pin_id
                )

        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def delete_temp_pin_image(self, pin_id):

    try:
        pin = Pin.objects.get(id=pin_id)

        if pin.temp_image:
            pin.temp_image.delete(save=False)
            pin.temp_image = None
            pin.save(update_fields=["temp_image"])

        return "Temporary image deleted"

    except Pin.DoesNotExist:
        return "Pin not found"

    except Exception as exc:
        logger.exception(
            "Temporary image deletion failed for Pin %s. Retry %s/%s",
            pin_id,
            self.request.retries,
            self.max_retries
        )

        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def delete_pin_image(self, image_name):

    if not image_name:
        return "No image name provided"

    try:
        result = cloudinary.uploader.destroy(image_name)

        return result

    except Exception as exc:
        logger.exception(
            "Cloudinary image deletion failed for %s. Retry %s/%s",
            image_name,
            self.request.retries,
            self.max_retries
        )

        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def index_pin(self, pin_id):

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
        return "Pin not found"

    except Exception as exc:
        logger.exception(
            "Elasticsearch indexing failed for Pin %s. Retry %s/%s",
            pin_id,
            self.request.retries,
            self.max_retries
        )

        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def delete_pin_from_elasticsearch(self, pin_id):

    try:
        es.delete(
            index="pins",
            id=pin_id
        )

        return f"Pin {pin_id} deleted successfully"

    except NotFoundError:
        return "Pin not found"

    except Exception as exc:
        logger.exception(
            "Elasticsearch deletion failed for Pin %s. Retry %s/%s",
            pin_id,
            self.request.retries,
            self.max_retries
        )

        raise self.retry(exc=exc)
