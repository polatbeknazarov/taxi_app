from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+998933640767'. Up to 15 digits allowed.",
    )

    phone_number = models.CharField(
        max_length=18,
        validators=[phone_regex,],
        blank=False,
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    balance = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
    )
    passport = models.ImageField(upload_to='images/', blank=True)
    car_brand = models.CharField(max_length=50, blank=False)
    car_number = models.CharField(max_length=20, blank=False)
    is_driver = models.BooleanField(default=False)
