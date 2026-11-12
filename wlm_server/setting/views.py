import json
from datetime import timedelta

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from setting.models import Setting
from event.models import Event
from task.message import ActionType, MessageInfo, MessageQueue
from utils import util

@login_required
@api_view(['POST'])
def handle_info(request, ch: int):  # pylint: disable=too-many-locals
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    latest_setting = settings.CHANNEL_CACHE.get_setting(ch)
    exposure, period = latest_setting.exposure, latest_setting.period
    update_exposure = False
    notif = {}
    event_content = []
    req_data = request.data.copy()
    exposure_s = req_data.get('exposure', None)
    period_s = req_data.get('period', None)
    if exposure_s is not None:
        if exposure_s <= 0:
            return HttpResponse(status=422)
        if channel.max_exposure is not None and exposure_s > channel.max_exposure.total_seconds():
            return HttpResponse(status=422)
        exposure = timedelta(seconds=exposure_s)
        update_exposure = True
        notif['exposure'] = exposure_s
        event_content.append(f'exposure: {exposure_s * 1e3:.0f} ms')
    if period_s is not None:
        period = timedelta(seconds=period_s)
        notif['period'] = period_s
        event_content.append(f'period: {period_s:.3f} s')
    setting = Setting(channel=channel, exposure=exposure, period=period)
    setting.save()
    message = MessageInfo(ActionType.SETTING, ch,
                          {'setting': setting, 'update_exposure': update_exposure})
    message_queue.push(message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_setting', {'type': 'notify', 'message': json.dumps(notif)}
    )
    joined_event_content = ', '.join(event_content)
    util.record_event(
        Event.EventType.SETTING,
        f'{user.username} updated the setting of channel {ch} ({joined_event_content}).'
    )
    return HttpResponse(status=200)
