import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from lock.models import Lock
from event.models import Event
from utils import util

@util.lock_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def try_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_open=True)
    if channel is None:
        return HttpResponse(status=error_code)
    lock = Lock(user=user, channel=channel)
    lock.save()
    notif = {'locked': True, 'owner': user.username}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock', {'type': 'notify', 'message': json.dumps(notif)}
    )
    util.record_event(Event.EventType.LOCK, f'{user.username} acquired the lock of channel {ch}.')
    return HttpResponse(status=200)


@util.lock_synchronized
@login_required
@require_http_methods(['PUT'])
@api_view(['PUT'])
def release_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    lock = settings.CHANNEL_CACHE.get_lock(ch)
    lock.expires_at = timezone.now()
    lock.save()
    notif = {'locked': False, 'owner': None}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_lock', {'type': 'notify', 'message': json.dumps(notif)}
    )
    util.record_event(Event.EventType.LOCK, f'{user.username} released the lock of channel {ch}.')
    return HttpResponse(status=200)
