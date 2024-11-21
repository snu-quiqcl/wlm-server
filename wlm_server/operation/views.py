import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from operation.models import Operation
from channel.models import Channel
from task.message import ActionType, MessageInfo, MessageQueue
from task.handler import TaskHandler
from utils import util

@login_required
@api_view(['POST'])
def handle_info(request, ch: int):
    user = request.user
    try:
        channel = Channel.objects.get(channel=ch)
    except Channel.DoesNotExist:
        return HttpResponse(status=404)
    if not channel.teams.contains(user.team):
        return HttpResponse(status=403)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    req_data = request.data.copy()
    on = req_data['on']
    operation = Operation(user=user, channel=channel, on=on)
    if on:
        if not util.is_wlm_running():
            task_handler = TaskHandler()
            task_handler.start()
        if not util.is_channel_running(ch):
            message = MessageInfo(ActionType.OPERATE, ch, {'on': True})
            message_queue.push(message)
            notif = {'on': True}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'channel_{ch}_operation', {'type': 'notify', 'message': json.dumps(notif)}
            )
        operation.save()
    else:
        operation.save()
        if not util.is_channel_running(ch):
            message = MessageInfo(ActionType.OPERATE, ch, {'on': False})
            message_queue.push(message)
            notif = {'on': False}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'channel_{ch}_operation', {'type': 'notify', 'message': json.dumps(notif)}
            )
        if not util.is_wlm_running():
            message = MessageInfo(ActionType.CLOSE, None, None)
            message_queue.push(message)
    return HttpResponse(status=200)
