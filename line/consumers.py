import json

from asgiref.sync import sync_to_async
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import AsyncWebsocketConsumer

from line.models import Line
from line.serializers import LineSerializer
from orders.models import Order, OrdersHistory, Client
from orders.serializers import OrderSerializer
from orders.tasks import send_sms
from dispatcher.models import Pricing


User = get_user_model()


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
        pass
        # try:
        #     line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
        #     await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

        #     await self.channel_layer.group_discard(
        #         self.username, self.channel_name
        #     )
        #     await self._send_line_disconnect()
        # except Exception as e:
        #     print(e)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'accept':
            await self._handle_accept_order(data)

        if data['type'] == 'join_line':
            await self._handle_join_line(data)

        if data['type'] == 'disconnect':
            await self._leave_line()

    async def _send_line_to_driver(self):
        line = await sync_to_async(Line.objects.filter)(status=True, from_city=self.from_city, to_city=self.to_city)
        data = await sync_to_async(self._serialize_line)(line)
        free_orders = await sync_to_async(Order.objects.filter)(
            from_city=self.from_city,
            to_city=self.to_city,
            is_free=True,
            in_search=True,
        )
        free_orders_data = await sync_to_async(self._serialize_free_orders)(free_orders)

        for driver in line:
            await self.channel_layer.group_send(
                driver.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps(
                        {
                            'line': data,
                        }
                    ),
                },
            )
            await self.channel_layer.group_send(
                driver.driver.username,
                {
                    'type': 'send_message',
                    'message': json.dumps(
                        {
                            'free_orders': free_orders_data,
                        }
                    ),
                },
            )

    async def _leave_line(self):
        line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
        await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

        await self.channel_layer.group_discard(
            self.username, self.channel_name
        )
        await self._send_line_disconnect()

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

            if not line_obj.status:
                line_obj.from_city = self.from_city
                line_obj.to_city = self.to_city
                line_obj.status = True
                line_obj.passengers = 0

                await sync_to_async(line_obj.save)()
        except ObjectDoesNotExist:
            await sync_to_async(Line.objects.create)(
                driver=self.user,
                from_city=self.from_city,
                to_city=self.to_city,
            )

    async def _remove_driver_from_line(self):
        line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
        await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

        await self.channel_layer.group_discard(
            self.username,
            self.channel_name,
        )

    def _serialize_line(self, line):
        serializer = LineSerializer(line, many=True)

        return serializer.data

    def _serialize_free_orders(self, free_order):
        serializer = OrderSerializer(free_order, many=True)

        return serializer.data

    async def _handle_accept_order(self, data):
        order_id = data['order_id']
        pricing = await sync_to_async(Pricing.get_singleton)()

        order = await sync_to_async(Order.objects.get)(id=order_id)
        driver = await sync_to_async(Line.objects.get)(driver=self.user)
        client = await sync_to_async(Client.objects.get)(id=order.client_id)
        user = await sync_to_async(User.objects.get)(id=self.user.id)

        price = float(order.passengers) * float(pricing.order_fee)

        if float(user.balance) - price < 0:
            await self.channel_layer.group_send(
                self.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'type': 'rejected', 'detail': f'Insufficient funds. Your balance: {self.user.balance}'}),
                },
            )
            return

        if order.in_search:
            order.driver = self.user

            order.in_search = False
            order.is_free = False

            count = await sync_to_async(Order.objects.filter(client=client).count)()

            if count == 1:
                client.balance = F('balance') + float(10000)
            else:
                client.balance = F('balance') + pricing.order_bonus

            driver.passengers += order.passengers
            user.balance = F('balance') - price

            await sync_to_async(driver.save)(update_fields=['passengers',])
            await sync_to_async(client.save)()

            await sync_to_async(client.refresh_from_db)()
            client_balance_value = client.balance
            await sync_to_async(send_sms.delay)(phone_number=client.phone_number, balance=client_balance_value)
            await sync_to_async(order.save)()
            await sync_to_async(user.save)()

            await sync_to_async(OrdersHistory.objects.create)(driver=self.user, order=order)

            if driver.passengers == 4:
                await self._completed_driver()

            await self._send_line_to_driver()

            await self.channel_layer.group_send(
                self.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'type': 'accepted', 'order_id': order_id}),
                },
            )

    async def _handle_join_line(self, data):
        price = await sync_to_async(Pricing.get_singleton)()
        if float(self.user.balance) > float(price.order_fee):
            self.from_city = data['from_city']
            self.to_city = data['to_city']

            await self._add_driver_to_line()
            await self._send_line_to_driver()
        else:
            await self.channel_layer.group_send(
                self.username,
                {
                    'type': 'send_message',
                    'message': json.dumps({'type': 'rejected', 'detail': f'Insufficient funds. Your balance: {self.user.balance}'}),
                },
            )

    async def _completed_driver(self):
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

    async def send_message(self, event):
        message = event['message']

        await self.send(message)
