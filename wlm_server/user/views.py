from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import UserInfoSerializer

@api_view(['POST'])
def sign_in(request):
    req_data = request.data.copy()
    username = req_data['username']
    password = req_data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        user_data = UserInfoSerializer(user).data
        data = {'user': user_data}
        return Response(data)
    return HttpResponse(status=401)


@login_required
@api_view(['POST'])
def sign_out(request):
    logout(request)
    return HttpResponse(status=200)


@login_required
@api_view(['GET'])
def handle_info(request):
    user = request.user
    data = UserInfoSerializer(user).data
    return Response(data)
