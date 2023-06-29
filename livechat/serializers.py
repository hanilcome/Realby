from rest_framework import serializers
from livechat.models import BlogRoom


class BlogRoomSerializer(serializers.ModelSerializer):
    """Blog Room serializer"""

    class Meta:
        model = BlogRoom
        fields = "__all__"
        
        
class BlogRoomCreateSerializer(serializers.ModelSerializer):
    """Blog Room create serializer"""

    class Meta:
        model = BlogRoom
        fields = ""
        
        
class BlogRoomActiceSerializer(serializers.ModelSerializer):
    """Blog Room create serializer"""

    class Meta:
        model = BlogRoom
        fields = ""