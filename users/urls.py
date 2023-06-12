from django.urls import path
from users import views
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("subscribe/<int:user_id>/", views.SubscribeView.as_view(), name="user_subscribe_view"),
]