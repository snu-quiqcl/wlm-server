from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from camel_converter import dict_to_camel

from channel.models import Channel
from channel.serializer import ChannelInfoSerializer

@login_required
@api_view(['GET'])
def handle_info(request):
    user = request.user
    channels = Channel.objects.filter(teams=user.team)
    data = ChannelInfoSerializer(channels, many=True, context={'username': user.username}).data
    return Response([dict_to_camel(info) for info in data])
