import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from line.models import Line
from line.serializers import LineSerializer
from orders.models import Order


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
            driver = await sync_to_async(Line.objects.filter)(driver=self.user)
            await sync_to_async(driver.update)(status=False)
            await self.channel_layer.group_discard(
                self.username, self.channel_name
            )
        except Exception as e:
            print(e)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'accept':
            order_id = data['order_id']

            order = await sync_to_async(Order.objects.get)(id=order_id)
            order.driver = self.user
            order.in_search = False
            order.balance += 1000
            await sync_to_async(order.save)()

            await self.channel_layer.group_send(
                self.username,
                {
                    'type': 'send_message',
                    'message': 'True',
                },
            )

        if data['type'] == 'join_line':
            self.from_city = data['from_city']
            self.to_city = data['to_city']

            await self._send_line_to_driver()

    async def _send_line_to_driver(self):
        obj, created = await sync_to_async(Line.objects.get_or_create)(driver=self.user)

        if obj:
            obj.status = True
            await sync_to_async(obj.save)()

        line = await sync_to_async(Line.objects.filter)(status=True)
        data = await sync_to_async(self._serialize_line)(line)

        for driver in line:
            await self.channel_layer.group_send(
                driver.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps(data),
                },
            )

    def _serialize_line(self, line):
        serializer = LineSerializer(line, many=True)
        return serializer.data

    async def send_message(self, event):
        message = event['message']
        await self.send(message)
