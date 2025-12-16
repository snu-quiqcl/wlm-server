from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework.decorators import api_view
from camel_converter import dict_to_camel

from channel.models import Channel
from channel.serializers import ChannelInfoSerializer
from utils import util

@login_required
@require_http_methods(['GET'])
@api_view(['GET'])
def handle_info(request):
    user = request.user
    channels = Channel.objects.filter(teams=user.team)
    data = ChannelInfoSerializer(channels, many=True, context={'username': user.username}).data
    return Response([dict_to_camel(info) for info in data])


@login_required
@require_http_methods(['GET'])
@api_view(['GET'])
def handle_single_info(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch)
    if channel is None:
        return HttpResponse(status=error_code)
    data = ChannelInfoSerializer(channel, context={'username': user.username}).data
    return Response(dict_to_camel(data))
