from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class Pricing(models.Model):
    order_fee = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=1000,
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
        return f'Order fee: {self.order_fee}. Ordes bonus: {self.order_bonus}'
