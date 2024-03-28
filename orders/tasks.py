import time
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from orders.serializers import OrderSerizlizer
from orders.models import Order
from orders.utils import get_order
from line.models import Line


@shared_task
def send_order_to_user(order, driver_username):
    # data = OrderSerizlizer(order).data
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        driver_username,
        {
            'type': 'order_created',
            'message': 'data',
        }
    )


@shared_task
def send_order():
    lines = Line.objects.filter(status=True)
    order = get_order()

    if order is None:
        return

    for line in lines:
        if not order.in_search:
            break

        send_order_to_user.apply_async(args=[order, line.driver.username])
        time.sleep(50)

        order.refresh_from_db()
