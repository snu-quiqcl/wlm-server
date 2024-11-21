from datetime import timedelta

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from rest_framework.decorators import api_view

from setting.models import Setting
from channel.models import Channel
from task.message import ActionType, MessageInfo, MessageQueue

@login_required
@api_view(['POST'])
def handle_info(request, ch: int):
    user = request.user
    try:
        channel = Channel.objects.get(channel=ch)
    except Channel.DoesNotExist:
        return HttpResponse(status=404)
    if user.team not in channel.teams.all():
        return HttpResponse(status=403)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    latest_setting = Setting.objects.filter(channel__channel=ch).order_by('-created_at').first()
    if latest_setting is None:
        exposure, period = None, None
    else:
        exposure, period = latest_setting.exposure, latest_setting.period
    req_data = request.data.copy()
    if 'exposure' in req_data:
        exposure_s = req_data['exposure']
        exposure = timedelta(seconds=exposure_s)
        message = MessageInfo(ActionType.EXPOSURE, ch, {'exposure': exposure})
        message_queue.push(message)
    if 'period' in req_data:
        period_s = req_data['period']
        period = timedelta(seconds=period_s)
        message = MessageInfo(ActionType.PERIOD, ch, {'period': period})
        message_queue.push(message)
    setting = Setting(channel=channel, exposure=exposure, period=period)
    setting.save()
    return HttpResponse(status=200)
