from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from .models import User

class LoginViewSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email

        return token
    
class UserSubscribeSerializer(serializers.ModelSerializer):
    subscribes = serializers.StringRelatedField(many=True)
    my_subscribers = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "my_subscribers",
            "subscribes"
        )