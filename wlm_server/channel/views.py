from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view

from channel.models import Channel
from channel.serializer import ChannelInfoSerializer

@login_required
@api_view(['GET'])
def handle_info(request):
    user = request.user
    channels = Channel.objects.filter(teams=user.team)
    data = ChannelInfoSerializer(channels, many=True, context={'user': user}).data
    return Response(data)
