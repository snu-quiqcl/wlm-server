from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from cache.channel import ChannelCache
from utils import channel_control, util

@util.task_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def handle_info(request, ch: int):  # pylint: disable=too-many-locals, too-many-statements
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch)
    if channel is None:
        return HttpResponse(status=error_code)
    if request.data['on']:
        status_code = channel_control.turn_on_operation(user, channel)
    else:
        status_code = channel_control.turn_off_operation(user, channel)
    return HttpResponse(status=status_code)


@util.task_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def wrap_up(request):
    user = request.user
    channel_cache: ChannelCache = settings.CHANNEL_CACHE
    chs = [channel.channel for channel in user.teams.channels.all()]
    for ch in chs:
        # Turn off PID
        channel, _ = util.verify_channel_access_with_dac(user, ch, check_lock=True)
        if channel is not None and channel_cache.get_pid_operation(ch) is not None:
            status_code = channel_control.turn_off_pid(user, channel)
            if status_code != 200:
                return HttpResponse(status=status_code)
        # Release lock
        channel, _ = util.verify_channel_access(user, ch, check_lock=True)
        if channel is not None:
            status_code = channel_control.release_lock(user, channel)
            if status_code != 200:
                return HttpResponse(status=status_code)
        # Turn off operation
        channel, _ = util.verify_channel_access(user, ch)
        if channel is not None:
            status_code = channel_control.turn_off_operation(user, channel)
            if status_code != 200:
                return HttpResponse(status=status_code)
    return HttpResponse(status=200)
