from django.urls import path
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
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
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("accounts/kakao/", views.KakaoLogin.as_view(), name="kakao_login"),
    path("accounts/naver/", views.NaverLogin.as_view(), name="naver_login"),
    path("accounts/google/", views.GoogleLogin.as_view(), name="google_login"),
    path("accounts/github/", views.GithubLogin.as_view(), name="github_login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("profile/", views.MyProfileView.as_view(), name="myprofile_view"),
]
