from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view

@api_view(['POST'])
def sign_in(request):
    req_data = request.data.copy()
    username = req_data['username']
    password = req_data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)


@api_view(['POST'])
def sign_out(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=401)
