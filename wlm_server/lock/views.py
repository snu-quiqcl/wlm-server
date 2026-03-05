from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from utils import channel_control, util

@util.lock_synchronized
@login_required
@require_http_methods(['POST'])
@api_view(['POST'])
def try_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_open=True)
    if channel is None:
        return HttpResponse(status=error_code)
    status_code = channel_control.acquire_lock(user, channel)
    return HttpResponse(status=status_code)


@util.lock_synchronized
@login_required
@require_http_methods(['PUT'])
@api_view(['PUT'])
def release_lock(request, ch: int):
    user = request.user
    channel, error_code = util.verify_channel_access(user, ch, check_lock=True)
    if channel is None:
        return HttpResponse(status=error_code)
    status_code = channel_control.release_lock(user, channel)
    return HttpResponse(status=status_code)
