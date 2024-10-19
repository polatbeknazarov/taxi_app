import json

from asgiref.sync import sync_to_async
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import AsyncWebsocketConsumer
from decimal import Decimal
from geopy.distance import geodesic

from line.models import Line
from line.serializers import LineSerializer
from orders.models import Order, Client
from orders.tasks import send_sms
from dispatcher.models import Pricing


User = get_user_model()


class LineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()

            return

        self.user = self.scope["user"]
        self.username = self.user.username
        self.from_city = None
        self.to_city = None

        await self.channel_layer.group_add(self.username, self.channel_name)

        await self.accept()
        await self._check_status()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "join_line":
            await self._handle_join_line(data)

        if data["type"] == "disconnect":
            await self._leave_line()

        if data["type"] == "location_update":
            await self.update_location(data)

    async def _send_line_to_driver(self):
        line = await sync_to_async(Line.objects.filter)(
            status=True, from_city=self.from_city, to_city=self.to_city
        )
        data = await sync_to_async(self._serialize_line)(line)

        line_list = await sync_to_async(list)(line)

        for driver in line_list:
            driver_username = await sync_to_async(lambda d: d.driver.username)(driver)
            await self.channel_layer.group_send(
                driver_username,
                {
                    "type": "send_message",
                    "message": json.dumps(
                        {
                            "line": data,
                        }
                    ),
                },
            )

    async def _leave_line(self):
        line_obj = await sync_to_async(Line.objects.get)(driver=self.user)
        await sync_to_async(Line.objects.filter(pk=line_obj.pk).update)(status=False)

        await self._send_line_to_driver()

    async def _add_driver_to_line(self):
        try:
            line_obj = await sync_to_async(Line.objects.get)(driver=self.user)

            if not line_obj.status:
                line_obj.from_city = self.from_city
                line_obj.to_city = self.to_city
                line_obj.status = True
                line_obj.passengers = 0
                line_obj.passengers_required = self.passengers_required

                await sync_to_async(line_obj.save)()

                free_orders = await sync_to_async(list)(
                    Order.objects.filter(
                        in_search=True,
                        is_free=True,
                        from_city=self.from_city,
                        to_city=self.to_city,
                    )
                )

                if free_orders:
                    pricing = await sync_to_async(Pricing.get_singleton)()
                    user = await sync_to_async(User.objects.get)(id=self.user.id)
                    user_balance = float(user.balance)
                    order_fee = float(pricing.order_fee)

                    for order in free_orders:
                        new_passengers = float(order.passengers)
                        if (user_balance >= new_passengers * order_fee) and (
                            line_obj.passengers_required
                            >= line_obj.passengers + order.passengers
                        ):
                            price = float(order.passengers) * \
                                float(pricing.order_fee)
                            client = await sync_to_async(Client.objects.get)(
                                pk=order.client_id
                            )

                            order.driver = line_obj
                            order.is_free = False
                            order.in_search = False
                            line_obj.passengers += order.passengers
                            user.balance = F("balance") - price

                            count = await sync_to_async(
                                Order.objects.filter(client=client).count
                            )()

                            if count == 1:
                                client.balance = F("balance") + float(10000)
                            else:
                                client.balance = F(
                                    "balance") + pricing.order_bonus

                            await sync_to_async(user.save)(
                                update_fields=[
                                    "balance",
                                ]
                            )
                            await sync_to_async(line_obj.save)(
                                update_fields=[
                                    "passengers",
                                ]
                            )
                            await sync_to_async(order.save)()
                            await sync_to_async(client.save)()
                            await sync_to_async(line_obj.refresh_from_db)()
                            await sync_to_async(client.refresh_from_db)()

                            await sync_to_async(send_sms.delay)(
                                phone_number=client.phone_number,
                                message=f'Saqiy Taxi. Вам назначена "{user.car_brand} {user.car_number}" Номер таксиста: {user.phone_number}. Бонус: {client.balance} сум',
                            )
                            await sync_to_async(user.refresh_from_db)()

                if line_obj.passengers > 0:
                    await self.channel_layer.group_send(
                        user.username,
                        {
                            "type": "send_message",
                            "message": json.dumps(
                                {
                                    "type": "new_order",
                                }
                            ),
                        },
                    )
                if line_obj.passengers == line_obj.passengers_required:
                    await self._completed_driver()
        except ObjectDoesNotExist:
            await sync_to_async(Line.objects.create)(
                driver=self.user,
                from_city=self.from_city,
                to_city=self.to_city,
                passengers_required=self.passengers_required,
                passengers=0,
            )

    async def _check_status(self):
        driver = await sync_to_async(Line.objects.get)(driver=self.user)

        if driver and driver.status:
            line = await sync_to_async(Line.objects.filter)(
                status=True, from_city=driver.from_city, to_city=driver.to_city
            )
            data = await sync_to_async(self._serialize_line)(line)

            for driver in line:
                await self.channel_layer.group_send(
                    self.username,
                    {
                        "type": "send_message",
                        "message": json.dumps(
                            {
                                "line": data,
                            }
                        ),
                    },
                )
        else:
            await self.channel_layer.group_send(
                self.username,
                {
                    "type": "send_message",
                    "message": json.dumps({"type": "offline"}),
                },
            )

    def _serialize_line(self, line):
        serializer = LineSerializer(line, many=True)

        return serializer.data

    async def _handle_join_line(self, data):
        latitude = data["latitude"]
        longitude = data["longitude"]

        user_coords = (latitude, longitude)
        sb_coords = (42.934882, 59.770027)
        nk_coords = (42.460341, 59.617996)
        radius_km = 20

        if data["from_city"] == "NK":
            distance = geodesic(user_coords, nk_coords).km
            if not distance <= radius_km:
                await self.channel_layer.group_send(
                    self.username,
                    {
                        "type": "send_message",
                        "message": json.dumps(
                            {
                                "type": "rejected_coords",
                                "detail": f"Insufficient funds. Your balance: {self.user.balance}",
                            }
                        ),
                    },
                )

                return
        else:
            distance = geodesic(user_coords, sb_coords).km
            if not distance <= radius_km:
                await self.channel_layer.group_send(
                    self.username,
                    {
                        "type": "send_message",
                        "message": json.dumps(
                            {
                                "type": "rejected_coords",
                                "detail": f"Insufficient funds. Your balance: {self.user.balance}",
                            }
                        ),
                    },
                )

            return

        price = await sync_to_async(Pricing.get_singleton)()
        passengers_required = float(data["passengers_required"])

        if Decimal(self.user.balance) > Decimal(price.order_fee) * Decimal(
            passengers_required
        ):
            self.from_city = data["from_city"]
            self.to_city = data["to_city"]
            self.passengers_required = float(data["passengers_required"])

            await self._add_driver_to_line()
            await self._send_line_to_driver()
        else:
            await self.channel_layer.group_send(
                self.username,
                {
                    "type": "send_message",
                    "message": json.dumps(
                        {
                            "type": "rejected",
                            "detail": f"Insufficient funds. Your balance: {self.user.balance}",
                        }
                    ),
                },
            )

    async def _completed_driver(self):
        line_obj = await sync_to_async(Line.objects.get)(driver=self.user)

        line_obj.status = False
        line_obj.passengers = 0
        line_obj.save(
            update_fields=[
                "status",
                "passengers",
            ]
        )

        await self.channel_layer.group_send(
            self.username,
            {"type": "send_message", "message": json.dumps(
                {"type": "completed"})},
        )

        await self.channel_layer.group_discard(self.username, self.channel_name)

    async def update_location(self, data):
        await self.channel_layer.group_send(
            "operators_group",
            {"type": "location_update", "driver": data},
        )

    async def send_message(self, event):
        message = event["message"]

        await self.send(message)


class MapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "update_map"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "location_update":
            latitude = data["data"]["latitude"]
            longitude = data["data"]["longitude"]
            user_id = data["user_id"]
            first_name = data["first_name"]
            last_name = data["last_name"]
            username = data["username"]
            car_number = data["car_number"]
            phone_number = data["phone_number"]

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "location_update",
                    "latitude": latitude,
                    "longitude": longitude,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "car_number": car_number,
                    "phone_number": phone_number,
                },
            )

    async def location_update(self, event):
        latitude = event["latitude"]
        longitude = event["longitude"]
        user_id = event["user_id"]
        first_name = event["first_name"]
        last_name = event["last_name"]
        username = event["username"]
        car_number = event["car_number"]
        phone_number = event["phone_number"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "location_update",
                    "latitude": latitude,
                    "longitude": longitude,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "car_number": car_number,
                    "phone_number": phone_number,
                }
            )
        )
