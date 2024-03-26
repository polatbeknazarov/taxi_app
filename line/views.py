from rest_framework.views import APIView, Response
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class TestAPIView(APIView):
    def get(self, request):
        channel_layer = get_channel_layer()
        groupts = async_to_sync(channel_layer.group_channels)()
        print('groupts', groupts)
        async_to_sync(channel_layer.group_send)(
            'root',
            {
                'type': 'send_message',
                'message': 'WAWAWAWAWAWWAWAWWA'
            }
        )
        return Response('hello')
