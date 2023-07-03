from rest_framework import serializers
from blogs.models import *
from users.models import User


class BackArticleSerializer(serializers.ModelSerializer):
    blog = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_blog(self, obj):
        return obj.blog.blog_name

    def get_user(self, obj):
        return obj.user.username

    def get_category(self, obj):
        if obj.category:
            return obj.category.category
        else:
            pass

    """BackArticle serializer"""

    class Meta:
        model = Article
        fields = "__all__"