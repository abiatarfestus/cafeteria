from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from PIL import Image


def validate_cellphone(value):
    """
    Validate whether the cellphone number is a valid MTC/TN number
    """
    # print(F"VALUE: {value}")
    if len(value) < 10:
        raise ValidationError(
            _(f"Cellphone number must have 10 digits."),
            params={"value": value},
        )
    elif value[:3] not in ["081", "085"]:
        raise ValidationError(
            _(f"A valid cellphone number must start with '081' or '085'"),
            params={"value": value},
        )
    for digit in value:
        if digit not in "0123456789":
            raise ValidationError(
                _(f"Cellphone number must contain digits only."),
                params={"value": value},
            )


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile",
    )  # Delete profile when user is deleted
    cellphone = models.CharField(
        max_length=10, null=True, validators=[validate_cellphone]
    )
    image = ResizedImageField(
        default="profile_pics/default.png",
        quality=100,
        size=[200, 200],
        upload_to="profile_pics",
    )

    def __str__(self):
        return f"{self.user.username} Profile"  # show how we want it to be displayed
