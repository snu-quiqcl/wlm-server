from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from config.models import Config
from utils import util

@login_required
@api_view(['POST'])
def calibrate(request):
    config = Config.objects.first()
    user = request.user
    channel, error_code = util.verify_channel_access(user, config.calib_ch)
    if channel is None:
        return HttpResponse(status=error_code)
    if util.is_wlm_running:
        return HttpResponse(409)
