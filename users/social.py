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
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.decorators import api_view
from .models import User
from .serializers import LoginViewSerializer
from rest_framework import status
from rest_framework.response import Response
import requests
from rest_framework.views import APIView
import json
from rest_framework.exceptions import APIException

# from dj_rest_auth.serializers import SocialLoginSerializer
# TwitterLoginSerializer만 따로 있고 나머지는 시리얼라이저 필요 없음.
# (dj-rest-auth 공식문서 참고)


# 소셜 로그인 사용자 정보 전송 URL
GOOGLE_CALLBACK_URI = os.getenv("FRONTEND_BASE_URL") + os.getenv(
    "GOOGLE_SOCIAL_CALLBACK_URI"
)
KAKAO_CALLBACK_URI = os.getenv("FRONTEND_BASE_URL") + os.getenv(
    "KAKAO_SOCIAL_CALLBACK_URI"
)
NAVER_CALLBACK_URI = os.getenv("FRONTEND_BASE_URL") + os.getenv(
    "NAVER_SOCIAL_CALLBACK_URI"
)
GITHUB_CALLBACK_URI = os.getenv("FRONTEND_BASE_URL") + os.getenv(
    "GITHUB_SOCIAL_CALLBACK_URI"
)
KAKAO_SOCIAL_LOGOUT_URI = os.getenv("FRONTEND_BASE_URL") + os.getenv(
    "KAKAO_SOCIAL_LOGOUT_URI"
)


# 추후 개발 예정
# 구글 소셜 로그인

# class GoogleLogin(SocialLoginView):
#     """
#     구글 소셜 로그인
#     """

#     adapter_class = GoogleOAuth2Adapter
#     callback_url = GOOGLE_CALLBACK_URI
#     client_class = OAuth2Client


# 카카-오 소셜 로그인
def kakao_login(request):
    """인가 코드 받기 요청"""

    client_id = os.getenv("KAKAO_REST_API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email,profile_nickname,profile_image"
    )


def kakao_logout(request):
    """인가 코드 받기 요청"""

    client_id = os.getenv("KAKAO_REST_API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/logout?client_id={client_id}&logout_redirect_uri={KAKAO_SOCIAL_LOGOUT_URI}"
    )


@api_view(["GET", "POST"])
def kakao_callback(request):
    """
    (인가 코드로) 토큰 발급 요청
    Access token, Refresh token
    """
    client_id = os.getenv("KAKAO_REST_API_KEY")
    code = request.data["code"]
    # code로 access token 요청
    token_request = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}"
    )

    token_request_json = token_request.json()
    # 에러 발생 시 중단
    error = token_request_json.get("error")
    if error is not None:
        raise json.JSONDecodeError("Error occurred during JSON decoding.", "", 0)

    access_token = token_request_json.get("access_token")

    requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    """
    로그인 처리, 토큰 정보 조회 및 검증
    """
    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None)  # 이메일!
    profile = kakao_account.get("profile")
    profile_img = profile.get("profile_image_url", None)
    username = profile.get("nickname", None)

    # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
    # if email is None:
    #     return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        if user.is_active == False:
            return Response(status=status.HTTP_403_NOT_ACCEPTABLE)

        refresh_token = LoginViewSerializer.get_token(user)
        return Response(
            data={
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token),
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email, username=username, profile_img=profile_img
        )
        user.email = email
        user.is_active = True
        user.user_type = User.UserTypeChoices.KAKAO
        user.save()
        refresh_token = LoginViewSerializer.get_token(user)
        return Response(
            data={
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token),
            },
            status=status.HTTP_200_OK,
        )


class CustomJSONDecodeError(APIException):
    status_code = 500  # 오류 상태 코드
    default_detail = "Error occurred during JSON decoding."  # 오류 메시지


# class KakaoLogin(SocialLoginView):
#     """카카오 소셜 로그인"""

#     adapter_class = KakaoOAuth2Adapter
#     callbakc_url = KAKAO_CALLBACK_URI
#     client_class = OAuth2Client

#     def post(self, request, *args, **kwargs):
#         print(1)
#         print(request.data)
#         accept = super().post(request, *args, **kwargs)
#         print(2)
#         accept_status = accept.status_code
#         print(3)
#         if accept_status != 200:
#             raise CustomJSONDecodeError()

#         user = User.objects.get(email=request.data["email"])
#         if user.is_active:
#             print(4)
#             refresh_token = LoginViewSerializer.get_token(user)
#             return Response(
#                 data={
#                     "refresh_token": str(refresh_token),
#                     "access_token": str(refresh_token.access_token),
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response({"message": "없는 유저입니다"}, status=status.HTTP_400_BAD_REQUEST)


# 추후 개발 예정
# 네이버 소셜 로그인

# class NaverLogin(SocialLoginView):
#     """
#     네이버 소셜 로그인
#     """

#     adapter_class = NaverOAuth2Adapter
#     callback_url = NAVER_CALLBACK_URI
#     client_class = OAuth2Client


# 추후 개발 예정
# 깃허브 소셜 로그인

# class GithubLogin(SocialLoginView):
#     """
#     깃허브 소셜 로그인
#     """

#     adapter_class = GitHubOAuth2Adapter
#     callback_url = GITHUB_CALLBACK_URI
#     client_class = OAuth2Client
