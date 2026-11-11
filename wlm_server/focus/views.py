import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from cache.channel import ChannelCache
from event.models import Event
from task.message import ActionType, MessageInfo, MessageQueue
from utils import util

@util.task_synchronized
@login_required
@api_view(['POST'])
def handle_info(request, ch: int):
    """Focuses or unfocuses the given channel.

    While a channel is focused, the WLM measures only that channel and the other channels are
    paused. Only the lock holder of the channel can change its focus, and only one channel can be
    focused at a time.
    """
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    on = request.data.get('on', None)
    if not isinstance(on, bool):
        return HttpResponse(status=400)
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    focused_channel = channel_cache.get_focused_channel()
    if focused_channel not in (None, ch):
        return HttpResponse(status=409)
    new_focused_channel = ch if on else None
    if new_focused_channel == focused_channel:
        return HttpResponse(status=200)
    event_content = f'{user.username} {"focused" if on else "unfocused"} channel {ch}.'
    channel_cache.set_focused_channel(new_focused_channel)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    message_queue.push(MessageInfo(ActionType.FOCUS, new_focused_channel, None))
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'focus', {'type': 'notify', 'message': json.dumps({'channel': new_focused_channel})}
    )
    util.record_event(Event.EventType.OPERATION, event_content)
    return HttpResponse(status=200)
