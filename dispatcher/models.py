from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model


User = get_user_model()


class Pricing(models.Model):
    order_fee = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=2000,
    )
    order_bonus = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=1000,
    )

    @classmethod
    def get_singleton(cls):
        try:
            return cls.objects.get()
        except ObjectDoesNotExist:
            return cls.objects.create()

    def __str__(self) -> str:
        return f"Order fee: {self.order_fee}. Ordes bonus: {self.order_bonus}"


class DriverBalanceHistory(models.Model):
    TYPE_CHOICES = [
        ("+", "Plus"),
        ("-", "Minus"),
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    transaction = models.CharField(max_length=2, choices=TYPE_CHOICES, blank=False)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Balance History"
        verbose_name_plural = "Balance Histories"
