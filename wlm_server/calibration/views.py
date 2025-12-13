from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from config.models import Config
from event.models import Event
from task.message import ActionType, MessageInfo, MessageQueue
from task.handler import TaskHandler
from utils import util

@util.task_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def calibrate(request):
    config = Config.objects.first()
    user = request.user
    channel, error_code = util.verify_channel_access(user, config.calib_ch, check_open=True)
    if channel is None:
        return HttpResponse(status=error_code)
    if util.is_wlm_running():
        return HttpResponse(status=409)
    message_queue: MessageQueue = settings.MESSAGE_QUEUE
    task_handler = TaskHandler()
    task_handler.start()
    message = MessageInfo(ActionType.CALIB, config.calib_ch,
                          {'exposure': config.calib_exposure, 'freq': config.calib_freq})
    message_queue.push(message)
    message = MessageInfo(ActionType.CLOSE, None, None)
    message_queue.push(message)
    util.record_event(Event.EventType.OPERATION, 'WLM calibrated.')
    return HttpResponse(status=200)
