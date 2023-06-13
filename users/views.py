from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from users.serializers import *

class LoginView(TokenObtainPairView):
    """로그인 정보 전송 및 처리 요청"""
    serializer_class = LoginViewSerializer
    