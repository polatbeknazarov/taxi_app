import json

from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from line.models import Line
from line.serializers import LineSerializer
from orders.models import Order, OrdersHistory, Client


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
            line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
            await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

            await self.channel_layer.group_discard(
                self.username, self.channel_name
            )
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
        line = await sync_to_async(Line.objects.filter)(status=True, from_city=self.from_city, to_city=self.to_city)
        data = await sync_to_async(self._serialize_line)(line)

        for driver in line:
            await self.channel_layer.group_send(
                driver.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps(
                        {
                            'line': data
                        }
                    ),
                },
            )

    async def _send_line_disconnect(self):
        try:
            line = await sync_to_async(Line.objects.filter)(status=True, from_city=self.from_city, to_city=self.to_city)
            data = await sync_to_async(self._serialize_line)(line)

            for driver in line:
                await self.channel_layer.group_send(
                    driver.driver.username,
                    {
                        'type': 'send_message',
                        'message': json.dumps({
                            'line': data
                        }),
                    },
                )
        except Exception as e:
            print('Send line is disconnect:', e)

    async def _add_driver_to_line(self):
        try:
            line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
            await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(
                from_city=self.from_city, to_city=self.to_city, status=True, joined_at=datetime.utcnow(), passengers=0
            )
        except Exception as e:
            await sync_to_async(Line.objects.create)(driver=self.user, from_city=self.from_city, to_city=self.to_city)
    
    
    async def _remove_driver_from_line(self):
        # driver = await sync_to_async(Line.objects.get)(driver=self.user)
        # driver.status = False

        line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
        await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

        await self.channel_layer.group_discard(
            self.username, self.channel_name
        )

    def _serialize_line(self, line):
        serializer = LineSerializer(line, many=True)

        return serializer.data

    async def _handle_accept_order(self, data):
        order_id = data['order_id']

        order = await sync_to_async(Order.objects.get)(id=order_id)
        driver = await sync_to_async(Line.objects.get)(driver=self.user)
        client = await sync_to_async(Client.objects.get)(id=order.client_id)

        order.driver = self.user
        order.in_search = False
        client.balance += 1000
        driver.passengers += order.passengers

        await sync_to_async(driver.save)()
        await sync_to_async(client.save)()

        if driver.passengers >= 4:
            line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
            await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

            await self.channel_layer.group_send(
                self.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'type': 'completed'})
                }
            )

            await self.channel_layer.group_add(
                self.username, self.channel_name
            )

        await self._send_line_to_driver()

        await sync_to_async(OrdersHistory.objects.create)(driver=self.user, client=order)
        await sync_to_async(order.save)()

        await self.channel_layer.group_send(
            self.username,
            {
                'type': 'send_message',
                'message': json.dumps({'type': 'accepted', 'order_id': order_id}),
            },
        )

    async def _handle_join_line(self, data):
        self.from_city = data['from_city']
        self.to_city = data['to_city']

        await self._add_driver_to_line()
        await self._send_line_to_driver()

    async def send_message(self, event):
        message = event['message']

        await self.send(message)
