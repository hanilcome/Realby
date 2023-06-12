from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from users.serializers import LoginViewSerializer, UserSubscribeSerializer


class LoginView(TokenObtainPairView):
    """로그인 정보 전송 및 처리 요청"""
    serializer_class = LoginViewSerializer
    
class SubscribeView(APIView):
    """구독한 특정 유저의 이름, 아이디 목록을 반환"""
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSubscribeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """특정 유저를 구독함"""
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if me != you:
            if me in you.my_subscribers.all():
                you.my_subscribers.remove(me)
                return Response("구독 취소", status=status.HTTP_204_NO_CONTENT)
            else:
                you.my_subscribers.add(me)
                return Response("구독", status=status.HTTP_200_OK)
        else:
            return Response(
                "자기 자신은 구독 할 수 없습니다!", status=status.HTTP_205_RESET_CONTENT
            )