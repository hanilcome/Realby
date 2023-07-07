from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import random, string
from .models import User
from .tokens import user_verify_token
from django.http import HttpResponse


# 랜덤 영문숫자 6글자의 비밀번호를 return하는 함수
def reset_password():
    new_str = string.ascii_letters + string.digits
    return "".join(random.choice(new_str) for _ in range(6))


class LoginViewSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # refresh token, access token 생성
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Refresh Token을 HTTP-only 쿠키에 저장
        refresh_token = data["refresh"]
        self.set_cookie("refresh", refresh_token)  # ("쿠키 키값", 쿠키값) 

        # Access Token을 헤더에 담아 전달
        access_token = data["access"]
        self.set_header("Authorization", f"Bearer {access_token}")

        return data

    def set_cookie(self, key, value):
        response = HttpResponse()
        response.set_cookie(key, value, httponly=True)
        self._response = response

    def set_header(self, key, value):
        response = HttpResponse()
        response[key] = value
        self._response = response


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()

        # url에 포함될 user.id 에러 방지용  encoding하기
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        # tokens.py에서 함수 호출
        token = user_verify_token.make_token(user)
        to_email = user.email
        email = EmailMessage(
            f"RealBy : {user.username}님의 이메일 인증",
            f"아래의 링크를 눌러 이메일 인증을 완료해주세요.\n\nhttp://0.0.0.0:3000/auth/emailverify/{uidb64}/{token}",
#             f"아래의 링크를 눌러 이메일 인증을 완료해주세요.\n\nhttps:www.realbyback.shop/users/verify/{uidb64}/{token}",
            to=[to_email],
        )
        email.send()
        return user


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)

    def update(self, instance, validated_data):
        password = reset_password()
        instance.set_password(password)
        instance.save()

        to_email = instance.email
        email = EmailMessage(
            "RealBy : 비밀번호 변경 안내",
            f"변경된 임시 비밀번호는 {password} 입니다. \n\n 로그인 후 반드시 회원정보 수정에서 비밀번호를 변경해주세요.",
            to=[to_email],
        )
        email.send()

        return instance


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "birthdate", "profile_img")
        read_only_fields = [
            "email",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
            "username": {
                "required": False,
            },
        }

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
