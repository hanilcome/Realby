from django.urls import path
from users import views, social

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("signup/", views.UserView.as_view(), name="user_view"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        views.EmailVerifyView.as_view(),
        name="email_verify_view",
    ),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("kakao/login/", social.KakaoLogin, name="kakao_login"),
    path("kakao/callback/", social.KakaoLogin.as_view(), name="kakao_login"),
    path("kakao/complete/", social.KakaoLogin.as_view(), name="kakao_login"),
    # 추후 개발 예정
    # path("naver/login/", social.NaverLogin.as_view(), name="naver_login"),
    # path("naver/callback/", social.NaverLogin.as_view(), name="naver_login"),
    # path("naver/complete/", social.NaverLogin.as_view(), name="naver_login"),
    # path("google/login/", social.GoogleLogin.as_view(), name="google_login"),
    # path("google/callback/", social.GoogleLogin.as_view(), name="google_login"),
    # path("google/complete/", social.GoogleLogin.as_view(), name="google_login"),
    # path("github/login/", social.GithubLogin.as_view(), name="github_login"),
    # path("github/callback/", social.GithubLogin.as_view(), name="github_login"),
    # path("github/complete/", social.GithubLogin.as_view(), name="github_login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("profile/", views.MyProfileView.as_view(), name="myprofile_view"),
]
