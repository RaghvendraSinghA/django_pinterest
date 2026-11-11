import logging
from celery import shared_task
from django.core.files import File
from .models import Profile


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def upload_profile_pic(self, profile_id):

    try:
        profile = Profile.objects.get(id=profile_id)

        if not profile.temp_profile_pic:
            return "No temporary profile picture found"

        # Keep the old image name so we can delete it after uploading
        # the new profile picture.
        old_image_name = (
            profile.profile_pic.name
            if profile.profile_pic else None
        )

        # Open the temporary image and upload it to permanent storage.
        with profile.temp_profile_pic.open("rb") as image_file:
            profile.profile_pic.save(
                profile.temp_profile_pic.name.split("/")[-1],
                File(image_file),
                save=False,
            )

        # Update the upload status after successfully saving the image.
        profile.upload_status = "uploaded"
        profile.save(update_fields=["profile_pic", "upload_status"])

        # Delete the previous image separately.
        # If this fails, don't retry the entire upload because the new
        # profile picture has already been saved successfully.
        if old_image_name:
            try:
                profile.profile_pic.storage.delete(old_image_name)
            except Exception:
                logger.exception(
                    "Failed to delete old profile picture %s for Profile %s",
                    old_image_name,
                    profile_id
                )

        # Schedule temporary image cleanup after five minutes.
        delete_temp_profile_pic.apply_async(
            args=[profile.id],
            countdown=300,
        )

        return "Profile picture uploaded successfully"

    except Profile.DoesNotExist:
        return "Profile not found"

    except Exception as exc:

        logger.exception(
            "Profile picture upload failed for Profile %s. Retry %s/%s",
            profile_id,
            self.request.retries,
            self.max_retries
        )

        # Mark the upload as failed after the final retry.
        if self.request.retries >= self.max_retries:
            try:
                profile = Profile.objects.get(id=profile_id)
                profile.upload_status = "failed"
                profile.save(update_fields=["upload_status"])

            except Exception:
                logger.exception(
                    "Could not update upload status for Profile %s",
                    profile_id
                )

        # Retry the task after an unexpected upload failure.
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def delete_temp_profile_pic(self, profile_id):

    try:
        profile = Profile.objects.get(id=profile_id)

        # Delete the temporary image from storage and clear its model field.
        if profile.temp_profile_pic:
            profile.temp_profile_pic.delete(save=False)
            profile.temp_profile_pic = None
            profile.save(update_fields=["temp_profile_pic"])

        return "Temporary profile picture deleted"

    except Profile.DoesNotExist:
        return "Profile not found"

    except Exception as exc:

        logger.exception(
            "Temporary profile picture deletion failed for Profile %s. Retry %s/%s",
            profile_id,
            self.request.retries,
            self.max_retries
        )

        # Retry temporary image deletion if an unexpected error occurs.
        raise self.retry(exc=exc)
