import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from operation.models import Operation
from event.models import Event
from task import message as task_message
from task.handler import TaskHandler
from pid import message as pid_message
from pid.handler import PidHandler
from cache.channel import ChannelCache
from utils import util

@util.task_synchronized
@login_required
@api_view(['POST'])
def handle_info(request, ch: int):  # pylint: disable=too-many-locals
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch)
    if channel is None:
        return HttpResponse(status=error_code)
    task_message_queue: task_message.MessageQueue = settings.MESSAGE_QUEUE
    pid_message_queue: pid_message.PidMessageQueue = settings.PID_MESSAGE_QUEUE
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    req_data = request.data.copy()
    on = req_data['on']
    operation = Operation(user=user, channel=channel, on=on)
    if on:
        util.record_event(Event.EventType.OPERATION,
                          f'{user.username} requested measurement of channel {ch}.')
        if not util.is_channel_running(ch):
            setting = channel_cache.get_setting(ch)
            message = task_message.MessageInfo(task_message.ActionType.SETTING, ch,
                                  {'setting': setting, 'update_exposure': True})
            task_message_queue.push(message)
            if not util.is_wlm_running():
                message = task_message.MessageInfo(task_message.ActionType.START, ch, None)
                task_message_queue.push(message)
                task_handler = TaskHandler()
                task_handler.start()
                util.record_event(Event.EventType.OPERATION, 'WLM started.')
                pid_handler = PidHandler()
                pid_handler.start()
                util.record_event(Event.EventType.PID, 'PID handler started.')
            message = task_message.MessageInfo(task_message.ActionType.OPERATE, ch, {'on': True})
            task_message_queue.push(message)
            util.record_event(Event.EventType.OPERATION, f'Measurement of channel {ch} started.')
        operation.save()
    else:
        util.record_event(Event.EventType.OPERATION,
                          f'{user.username} requested to stop the measurement of channel {ch}.')
        pid_operation = channel_cache.get_pid_operation(ch)
        if pid_operation is not None and pid_operation.user == user:
            util.record_event(
                Event.EventType.WARNING,
                f'Cannot stop operation for channel {ch} because {user.username} is performing a '
                'PID operation. This request has been ignored.'
            )
            return HttpResponse(status=409)
        operation.save()
        if not util.is_channel_running(ch):
            message = task_message.MessageInfo(task_message.ActionType.OPERATE, ch, {'on': False})
            task_message_queue.push(message)
            util.record_event(Event.EventType.OPERATION, f'Measurement of channel {ch} stopped.')
            if not util.is_wlm_running():
                message = task_message.MessageInfo(task_message.ActionType.STOP, None, None)
                task_message_queue.push(message)
                message = task_message.MessageInfo(task_message.ActionType.CLOSE, None, None)
                task_message_queue.push(message)
                util.record_event(Event.EventType.OPERATION, 'WLM stopped.')
                message = pid_message.PidMessageInfo(pid_message.ActionType.CLOSE, None)
                pid_message_queue.push(message)
                util.record_event(Event.EventType.PID, 'PID handler stopped.')
    requesters = [op.user.username for op in channel_cache.get_operations(ch).values() if op.on]
    notif = {'on': util.is_channel_running(ch), 'requesters': requesters}
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'channel_{ch}_operation', {'type': 'notify', 'message': json.dumps(notif)}
    )
    return HttpResponse(status=200)
