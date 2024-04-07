import json
import datetime

from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from line.models import Line
from line.serializers import LineSerializer
from orders.models import Order, OrdersHistory


class LineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            self.close()

            return

        self.user = self.scope['user']
        self.username = self.user.username
        self.from_city = None
        self.to_city = None

        await self.channel_layer.group_add(
            self.username, self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        try:
            await self._remove_driver_from_line()
            await self._send_line_disconnect()
        except Exception as e:
            print(e)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'accept':
            await self._handle_accept_order(data)

        if data['type'] == 'join_line':
            await self._handle_join_line(data)

    async def _send_line_to_driver(self):
        try:
            line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
            await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(
                from_city=self.from_city, to_city=self.to_city, status=True
            )
        except:
            await sync_to_async(Line.objects.create)(driver=self.user, from_city=self.from_city, to_city=self.to_city)

        line = await sync_to_async(Line.objects.filter)(status=True, from_city=self.from_city, to_city=self.to_city)
        data = await sync_to_async(self._serialize_line)(line)

        for driver in line:
            await self.channel_layer.group_send(
                driver.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps(data),
                },
            )

    async def _send_line_disconnect(self):
        try:
            line = await sync_to_async(Line.objects.filter)(status=True, from_city=self.from_city, to_city=self.to_city)
            await sync_to_async(print)('LINE', line)
            data = await sync_to_async(self._serialize_line)(line)

            for driver in line:
                await self.channel_layer.group_send(
                    driver.driver.username,
                    {
                        'type': 'send_message',
                        'message': json.dumps(data),
                    },
                )
        except Exception as e:
            print('Send line is disconnect:', e)

    async def _remove_driver_from_line(self):
        driver = await sync_to_async(Line.objects.filter)(driver=self.user)
        await sync_to_async(driver.update)(status=False)

        await self.channel_layer.group_discard(
            self.username, self.channel_name
        )

        return True

    def _serialize_line(self, line):
        serializer = LineSerializer(line, many=True)

        return serializer.data

    async def _handle_accept_order(self, data):
        order_id = data['order_id']

        order = await sync_to_async(Order.objects.get)(id=order_id)
        driver = await sync_to_async(Line.objects.get)(driver=self.user)

        if driver.passengers < 4:
            order.driver = self.user
            order.in_search = False
            order.balance += 1000

            driver.passengers += 1

            if driver.passengers == 4:
                await self._remove_driver_from_line()

            await sync_to_async(OrdersHistory.objects.create)(driver=self.user, client=order)
            await sync_to_async(order.save)()
        else:
            await self._remove_driver_from_line()

        await self.channel_layer.group_send(
            self.username,
            {
                'type': 'send_message',
                'message': 'True',
            },
        )

    async def _handle_join_line(self, data):
        self.from_city = data['from_city']
        self.to_city = data['to_city']

        await self._send_line_to_driver()

    async def send_message(self, event):
        message = event['message']

        await self.send(message)
