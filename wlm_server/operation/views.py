from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

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
