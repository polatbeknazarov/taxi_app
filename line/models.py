from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()


class Line(models.Model):
    CITY_CHOICES = [
        ('NK', 'Нукус'),
        ('SB', 'Шымбай'),
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_lines')
    from_city = models.CharField(
        max_length=2,
        choices=CITY_CHOICES,
        blank=False,
    )
    to_city = models.CharField(
        max_length=2,
        choices=CITY_CHOICES,
        blank=False,
    )
    passengers = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(4),
        ],
        default=0,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['joined_at',]

    def __str__(self) -> str:
        return str(self.driver)
