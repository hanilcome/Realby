from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models.query_utils import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from .tokens import user_verify_token
from .models import User
from users.serializers import (
    UserSerializer,
    UserPasswordSerializer,
    UserUpdateSerializer,
    LoginViewSerializer,
)
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.naver.views import NaverOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import os
from django.shortcuts import redirect
from json.decoder import JSONDecodeError
from django.conf import settings


# from dj_rest_auth.serializers import SocialLoginSerializer
# TwitterLoginSerializer만 따로 있고 나머지는 시리얼라이저 필요 없음.
# (dj-rest-auth 공식문서 참고)


class UserView(APIView):
    """회원가입 정보 전송 및 처리 요청"""

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "유저 인증용 이메일을 전송했습니다."}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


class EmailVerifyView(APIView):
    """이메일 인증"""

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if user_verify_token.check_token(user, token):
                User.objects.filter(pk=uid).update(is_active=True)
                return Response({"message": "이메일 인증 완료"}, status=status.HTTP_200_OK)
            return Response({"error": "인증 실패"}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "KEY ERROR"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """로그인 정보 전송 및 처리 요청"""

    serializer_class = LoginViewSerializer


# 소셜 로그인
BASE_URL = "http://localhost:8000/users/accounts/"
GOOGLE_CALLBACK_URI = BASE_URL + "google/callback/"
KAKAO_CALLBACK_URI = BASE_URL + "kakao/callback/"
NAVER_CALLBACK_URI = BASE_URL + "naver/callback/"
GITHUB_CALLBACK_URI = BASE_URL + "github/callback/"


class GoogleLogin(SocialLoginView):
    """구글 소셜 로그인"""

    adapter_class = GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


class KakaoLogin(SocialLoginView):
    """카카오 소셜 로그인"""

    adapter_class = KakaoOAuth2Adapter
    callbakc_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client

    """
    인가 코드 받기 요청
    """

    def kakao_login(request):
        client_id = settings.get_secret("SOCIAL_AUTH_KAKAO_CLIENT_ID")
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email"
        )

    """
    (인가 코드로) 토큰 발급 요청
    """

    def kakao_callback(request):
        client_id = settings.get_secret("SOCIAL_AUTH_KAKAO_CLIENT_ID")
        code = request.GET.get("code")

        # code로 access token 요청
        token_request = request.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}"
        )
        token_response_json = token_request.json()

        # 에러 발생 시 중단
        error = token_response_json.get("error", None)
        if error is not None:
            raise JSONDecodeError(error)

        access_token = token_response_json.get("access_token")

    """
    로그인 처리, 토큰 정보 조회 및 검증
    """

    def kakao_callback(request):
        # access token으로 카카오톡 프로필 요청
        profile_request = request.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()

        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)  # 이메일!

        # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
        # if email is None:
        #     return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)


class NaverLogin(SocialLoginView):
    """네이버 소셜 로그인"""

    adapter_class = NaverOAuth2Adapter
    callback_url = NAVER_CALLBACK_URI
    client_class = OAuth2Client


class GithubLogin(SocialLoginView):
    """깃허브 소셜 로그인"""

    adapter_class = GitHubOAuth2Adapter
    callback_url = GITHUB_CALLBACK_URI
    client_class = OAuth2Client


class MyProfileView(APIView):
    """유저 정보 요청, 수정, 회원 탈퇴"""

    """
    유저 정보 요청
    """

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    """
    유저 정보 수정
    """

    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    회원 탈퇴
    is_active = False로 변경만 하고 회원 정보는 계속 보관
    email(아이디), name 남아있어서 탈퇴한 회원이 같은 정보로 재가입 불가
    """

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user.id == user.id:
            user = request.user
            user.is_active = False
            user.save()
            return Response(
                {"message": "회원 탈퇴되었습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"message": "회원 탈퇴에 실패했습니다."}, status=status.HTTP_401_UNAUTHORIZED
            )


class UserPasswordView(APIView):
    """유저의 이메일 정보로 패스워드를 리셋"""

    def put(self, request):
        user = get_object_or_404(User, email=request.data.get("email"))
        serializer = UserPasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "비밀번호 수정 이메일을 전송했습니다."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
