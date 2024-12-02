import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from lock.models import Lock
from utils import util

@login_required
@api_view(['POST'])
def try_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch)
    if channel is None:
        return HttpResponse(status=error_code)
    lock = Lock(user=user, channel=channel)
    lock.save()
    notif = {'locked': True, 'username': user.username}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock', {'type': 'notify', 'message': json.dumps(notif)}
    )
    return HttpResponse(status=200)


@login_required
@api_view(['PUT'])
def release_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch)
    if channel is None:
        return HttpResponse(status=error_code)
    lock = settings.CHANNEL_CACHE.get_lock(ch)
    lock.expires_at = timezone.now()
    lock.save()
    notif = {'locked': False, 'username': None}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock', {'type': 'notify', 'message': json.dumps(notif)}
    )
    return HttpResponse(status=200)
