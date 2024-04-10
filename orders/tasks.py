import time
import json

from core.celery import app

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from orders.models import Order
from orders.serializers import OrderSerializer
from line.models import Line


@app.task
def send_order(order_id, from_city, to_city):
    lines = Line.objects.filter(status=True, from_city=from_city, to_city=to_city)
    order = Order.objects.get(id=order_id)
    data = OrderSerializer(order).data

    channel_layer = get_channel_layer()

    for line in lines:
        if not order.in_search:
            return

        async_to_sync(channel_layer.group_send)(
            line.driver.username,
            {
                'type': 'send_message',
                'message': json.dumps(data),
            }
        )

        time.sleep(15)
        order.refresh_from_db()
