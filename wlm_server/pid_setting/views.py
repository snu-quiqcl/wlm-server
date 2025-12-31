import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from camel_converter import dict_to_camel

from pid_setting.models import PidSetting
from event.models import Event
from pid.message import ActionType, PidMessageInfo, PidMessageQueue
from utils import util

@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def handle_info(request, ch: int):  # pylint: disable=too-many-locals
    user = request.user
    channel, error_code = util.verify_channel_access_with_dac(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    pid_message_queue: PidMessageQueue = settings.PID_MESSAGE_QUEUE
    latest_pid_setting = settings.CHANNEL_CACHE.get_pid_setting(ch)
    target_frequency = latest_pid_setting.target_frequency
    kp = latest_pid_setting.kp
    ki = latest_pid_setting.ki
    kd = latest_pid_setting.kd
    notif = {}
    event_content = []
    req_data = request.data.copy()
    target_frequency_new = req_data.get('target_frequency', None)
    kp_new = req_data.get('kp', None)
    ki_new = req_data.get('ki', None)
    kd_new = req_data.get('kd', None)
    if target_frequency_new is not None:
        target_frequency = target_frequency_new
        notif['target_frequency'] = target_frequency
        event_content.append(f'target_frequency: {target_frequency / 1e12:.6f} THz')
    if kp_new is not None:
        kp = kp_new
        notif['kp'] = kp
        event_content.append(f'kp: {kp * 1e9:.3f} × 10⁻⁹')
    if ki_new is not None:
        ki = ki_new
        notif['ki'] = ki
        event_content.append(f'ki: {ki * 1e9:.3f} × 10⁻⁹')
    if kd_new is not None:
        kd = kd_new
        notif['kd'] = kd
        event_content.append(f'kd: {kd * 1e9:.3f} × 10⁻⁹')
    pid_setting = PidSetting(
        channel=channel,
        target_frequency=target_frequency,
        kp=kp,
        ki=ki,
        kd=kd
    )
    pid_setting.save()
    message = PidMessageInfo(
        ActionType.SETTING,
        {'channel': ch, 'pid_setting': pid_setting}
    )
    pid_message_queue.push(message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_pid_setting', {'type': 'notify', 'message': json.dumps(dict_to_camel(notif))}
    )
    joined_event_content = ', '.join(event_content)
    util.record_event(
        Event.EventType.PID,
        f'{user.username} updated the PID setting of channel {ch} ({joined_event_content}).'
    )
    return HttpResponse(status=200)
