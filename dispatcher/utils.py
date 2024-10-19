import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from line.models import Line
from line.serializers import LineSerializer


def send_line(from_city, to_city):
    channel_layer = get_channel_layer()

    line = Line.objects.filter(
        status=True,
        from_city=from_city,
        to_city=to_city,
    )
    data = LineSerializer(line, many=True)

    for driver in line:
        async_to_sync(channel_layer.group_send)(
            driver.driver.username,
            {
                "type": "send_message",
                "message": json.dumps({"line": data.data}),
            },
        )
