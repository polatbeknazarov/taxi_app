import time
import json

from core.celery import app

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from orders.models import Order
from orders.serializers import OrderSerializer
from line.models import Line
from dispatcher.models import Pricing
from orders.utils import SendSmsWithEskizApi


@app.task
def send_order(order_id, from_city, to_city):
    pricing = Pricing.get_singleton()
    lines = Line.objects.filter(
        status=True, from_city=from_city, to_city=to_city)
    order = Order.objects.get(id=order_id)
    order_passengers = order.passengers
    data = OrderSerializer(order).data

    channel_layer = get_channel_layer()

    for line in lines:
        if not order.in_search:
            return

        passengers = line.passengers + order_passengers
        price = pricing.order_fee * order_passengers

        if passengers <= 4 and float(line.driver.balance) > price:
            async_to_sync(channel_layer.group_send)(
                line.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'order': data}),
                }
            )

            time.sleep(15)
            order.refresh_from_db()

            if order.in_search:
                async_to_sync(channel_layer.group_send)(
                    line.driver.username,
                    {
                        'type': 'send_message',
                        'message': json.dumps({'type': 'canceled'}),
                    }
                )

    if order.in_search:
        Order.objects.filter(pk=order.pk).update(is_free=True)

        free_orders = Order.objects.filter(is_free=True)
        free_orders_data = OrderSerializer(free_orders, many=True)

        for line in lines:
            async_to_sync(channel_layer.group_send)(
                line.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'free_orders': free_orders_data.data})
                }
            )


@app.task
def send_sms(phone_number='+998913930730', balance='1000'):
    message = f"Taksi Servis \"Saqiy Taxi\". Sizdin' ja'mi bonusin'iz: {balance}. Tel: 55 106-48-48, 77 106-48-48"

    eskiz_api = SendSmsWithEskizApi(
        message=message, phone=phone_number.replace('+', ''))
    eskiz_api.send_message()
