import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from line.models import Line
from line.serializers import LineSerializer


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
            driver = await sync_to_async(Line.objects.filter)(driver=self.user)
            await sync_to_async(driver.update)(status=False)
            await self.channel_layer.group_discard(
                self.username, self.channel_name
            )
        except Exception as e:
            print(e)

    async def receive(self, text_data):
        pass

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
