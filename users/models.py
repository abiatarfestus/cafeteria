from PIL import Image
from django.db import models
from django.contrib.auth.models import User
# from django_resized import ResizedImageField


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )  # Delete profile when user is deleted
    # image = ResizedImageField(
    #     default="profile_pics/default.apng",
    #     quality=100,
    #     size=[200, 200],
    #     upload_to="profile_pics",
    # )

    def __str__(self):
        return f"{self.user.username} Profile"  # show how we want it to be displayed