from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

from users.models import CustomUser


class Client(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: \'+998933640767\'. Up to 15 digits allowed.'
    )

    phone_number = models.CharField(
        max_length=18,
        validators=[phone_regex,],
        blank=False,
    )
    balance = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return str(self.phone_number)


class Order(models.Model):
    CITY_CHOICES = [
        ('NK', 'Нукус'),
        ('SB', 'Шымбай'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    from_city = models.CharField(
        max_length=2,
        choices=CITY_CHOICES,
        verbose_name='From',
        blank=False,
    )
    to_city = models.CharField(
        max_length=2,
        choices=CITY_CHOICES,
        verbose_name='To',
        blank=False,
    )
    passengers = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ],
        default=1,
    )
    address = models.TextField(blank=False)
    in_search = models.BooleanField(default=True)
    driver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Client: {self.client}. Order route: {self.from_city} - {self.to_city}'


class OrdersHistory(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Order History'
        verbose_name_plural = 'Order Histories'

    def __str__(self) -> str:
        return f'Driver: {self.driver} - Order: {self.order}'


# @receiver(post_save, sender=Order)
# def order_post_save(sender, instance, created, **kwargs):
#     from orders.tasks import send_order, send_message

#     send_order.delay(
#         order_id=instance.id,
#         from_city=instance.from_city,
#         to_city=instance.to_city,
#     )
#     send_message.delay(phone_number=instance.client.phone_number)
