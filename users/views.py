from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import LoginViewSerializer

class LoginView(TokenObtainPairView):
    """로그인 정보 전송 및 처리 요청"""

    serializer_class = LoginViewSerializer