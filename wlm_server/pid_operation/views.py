import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from pid_operation.models import PidOperation
from event.models import Event
from pid import message as pid_message
from cache.channel import ChannelCache
from utils import util

@util.task_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def handle_info(request, ch: int):  # pylint: disable=too-many-locals
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    req_data = request.data.copy()
    on = req_data['on']
    pid_operation = PidOperation(user=user, channel=channel, on=on)
    if on:
        util.record_event(Event.EventType.PID,
                          f'{user.username} requested to enable PID control for channel {ch}.')
        operations = channel_cache.get_operations(ch)
        if not user.username in operations:
            util.record_event(
                Event.EventType.WARNING,
                f'Cannot enable PID control for channel {ch} because {user.username} is not '
                'performing an operation. This request has been ignored.'
            )
            return HttpResponse(status=409)
        if util.is_channel_pid_enabled(ch):
            util.record_event(
                Event.EventType.WARNING,
                f'PID control for channel {ch} is already enabled. This request has been ignored.'
            )
            return HttpResponse(status=409)
        pid_setting = channel_cache.get_pid_setting(ch)
        if pid_setting is None:
            util.record_event(
                Event.EventType.WARNING,
                f'Cannot enable PID control for channel {ch} because no PID setting is set. '
                'This request has been ignored.'
            )
            return HttpResponse(status=409)
        message = pid_message.PidMessageInfo(
            pid_message.ActionType.SETTING, {'channel': ch, 'pid_setting': pid_setting})
        pid_message_queue.push(message)
        message = pid_message.PidMessageInfo(pid_message.ActionType.ON, {'channel': ch})
        pid_message_queue.push(message)
        util.record_event(Event.EventType.PID, f'PID control for channel {ch} enabled.')
        pid_operation.save()
    else:
        util.record_event(Event.EventType.PID,
                          f'{user.username} requested to disable PID control for channel {ch}.')
        pid_operation.save()
        if not util.is_channel_pid_enabled(ch):
            message = pid_message.PidMessageInfo(pid_message.ActionType.OFF, {'channel': ch})
            pid_message_queue.push(message)
            util.record_event(Event.EventType.PID, f'PID control for channel {ch} disabled.')
    return HttpResponse(status=200)
