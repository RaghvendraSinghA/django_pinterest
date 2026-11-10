# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import storages


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_pic = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    bio = models.TextField(
        max_length=300,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    temp_profile_pic = models.FileField(
        upload_to="temp/profile_pictures/",
        storage=storages["temp"],
        blank=True,
        null=True,  
    )

    UPLOAD_STATUS = [
        ("pending", "Pending"),
        ("uploaded", "Uploaded"),
        ("failed", "Failed"),
    ]

    upload_status = models.CharField(
        max_length=20,
        choices=UPLOAD_STATUS,
        default="uploaded",
    )

    def __str__(self):
        return f"{self.user.username}'s profile"
