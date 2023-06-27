from django.urls import path
from .views import *

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView,
# )

urlpatterns = [
    path("signup/", UserView.as_view(), name="user_view"),
    path(
        "verify/<str:uidb64>/<str:token>/",
        EmailVerifyView.as_view(),
        name="email_verify_view",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("accounts/kakao/", KakaoLogin.as_view(), name="kakao_login"),
    path("accounts/naver/", NaverLogin.as_view(), name="naver_login"),
    path("accounts/google/", GoogleLogin.as_view(), name="google_login"),
    path("accounts/github/", GithubLogin.as_view(), name="github_login"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("profile/", MyProfileView.as_view(), name="myprofile_view"),
]
