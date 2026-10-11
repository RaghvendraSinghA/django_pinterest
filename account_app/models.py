# Create your models here.

from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return f"{self.user.username}'s profile"
