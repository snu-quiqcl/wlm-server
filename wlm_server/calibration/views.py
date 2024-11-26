from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

from utils import util

@login_required
@api_view(['POST'])
def calibrate(request):
    if util.is_wlm_running:
        return HttpResponse(409)
