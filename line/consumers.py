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

        await self.channel_layer.group_add(
            self.username, self.channel_name
        )
        await self._send_line_to_driver()
        await self.accept()

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.username, self.channel_name
            )
            await sync_to_async(Line.objects.filter(driver=self.user).update)(status=False)
        except Exception as e:
            print(e)

    async def receive(self, event):
        pass

    async def _send_line_to_driver(self):
        await sync_to_async(Line.objects.create)(driver=self.user)

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

    async def order_created(self, order):
        await self.send_message({'message': json.dumps(order['message'])})
