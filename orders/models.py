from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

from users.models import CustomUser


class Order(models.Model):
    CITY_CHOICES = [
        ('NK', 'Нукус'),
        ('SB', 'Шымбай'),
    ]
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+998933640767'. Up to 15 digits allowed.")

    from_city = models.CharField(
        max_length=2, choices=CITY_CHOICES, default='NK', verbose_name='From', blank=False)
    to_city = models.CharField(
        max_length=2, choices=CITY_CHOICES, default='SB', verbose_name='To', blank=False)
    address = models.TextField(blank=False)
    phone_number = models.CharField(
        max_length=18, validators=[phone_regex,], blank=False)
    balance = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    in_search = models.BooleanField(default=True)
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.phone_number)


class OrdersHistory(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    client = models.ForeignKey(Order, on_delete=models.CASCADE)


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    from orders.tasks import send_order
    send_order.delay(
        order_id=instance.id,
        from_city=instance.from_city,
        to_city=instance.to_city,
    )
