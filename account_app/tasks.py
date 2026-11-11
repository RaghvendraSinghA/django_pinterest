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
            logger.warning(
                "No temporary profile picture found for Profile %s",
                profile_id
            )
            return "No temporary profile picture found"

        old_image_name = (
            profile.profile_pic.name
            if profile.profile_pic else None
        )

        with profile.temp_profile_pic.open("rb") as image_file:
            profile.profile_pic.save(
                profile.temp_profile_pic.name.split("/")[-1],
                File(image_file),
                save=False,
            )

        profile.upload_status = "uploaded"
        profile.save(update_fields=["profile_pic", "upload_status"])

        if old_image_name:
            profile.profile_pic.storage.delete(old_image_name)

        delete_temp_profile_pic.apply_async(
            args=[profile.id],
            countdown=300,
        )

        logger.info(
            "Profile picture uploaded successfully for Profile %s",
            profile_id
        )

        return "Profile picture uploaded successfully"

    except Profile.DoesNotExist:
        logger.warning(
            "Profile %s not found for profile picture upload",
            profile_id
        )
        return "Profile not found"

    except Exception as exc:

        logger.exception(
            "Profile picture upload failed for Profile %s. Retry %s/%s",
            profile_id,
            self.request.retries,
            self.max_retries
        )

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

        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10
)
def delete_temp_profile_pic(self, profile_id):

    try:
        profile = Profile.objects.get(id=profile_id)

        if profile.temp_profile_pic:
            profile.temp_profile_pic.delete(save=False)
            profile.temp_profile_pic = None
            profile.save(update_fields=["temp_profile_pic"])

        logger.info(
            "Temporary profile picture deleted for Profile %s",
            profile_id
        )

        return "Temporary profile picture deleted"

    except Profile.DoesNotExist:
        logger.warning(
            "Profile %s not found while deleting temporary picture",
            profile_id
        )
        return "Profile not found"

    except Exception as exc:

        logger.exception(
            "Temporary profile picture deletion failed for Profile %s. Retry %s/%s",
            profile_id,
            self.request.retries,
            self.max_retries
        )

        raise self.retry(exc=exc)
