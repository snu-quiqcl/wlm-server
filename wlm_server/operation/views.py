from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view

from operation.models import Operation
from channel.models import Channel
from task.message import ActionType, MessageInfo, MessageQueue
from task.handler import TaskHandler

def get_running_status(ch: int) -> tuple[bool, bool]:
    """Gets running status of WLM and the given channel.
    
    Args:
        ch: Target channel.

    Returns:
        Tuple with WLM running status and target channel running
    """
    latest_operations = (
        Operation.objects.order_by('channel', 'user', '-occured_at').distinct('channel', 'user')
    )  # latest operations for each channel and user
    is_wlm_running = any(op.on for op in latest_operations)
    is_channel_running = any(op.channel.channel == ch and op.on for op in latest_operations)
    return is_wlm_running, is_channel_running


@login_required
@api_view(['POST'])
def handle_info(request, ch: int):
    user = request.user
    channel = Channel.objects.get(channel=ch)
    if user.team not in channel.teams.all():
        return HttpResponse(status=403)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    req_data = request.data.copy()
    on = req_data['on']
    operation = Operation(user=user, channel=channel, on=on)
    if on:
        is_wlm_running, is_channel_running = get_running_status(ch)
        if not is_wlm_running:
            task_handler = TaskHandler()
            task_handler.start()
        if not is_channel_running:
            message = MessageInfo(ActionType.OPERATE, ch, {'on': True})
            message_queue.push(message)
        operation.save()
    else:
        operation.save()
        is_wlm_running, is_channel_running = get_running_status(ch)
        if not is_channel_running:
            message = MessageInfo(ActionType.OPERATE, ch, {'on': False})
            message_queue.push(message)
        if not is_wlm_running:
            message = MessageInfo(ActionType.CLOSE, None, None)
            message_queue.push(message)
    return HttpResponse(status=200)
