from rest_framework import serializers
from blogs.models import *
from users.models import User


class BlogSerializer(serializers.ModelSerializer):
    """Blog serializer"""

    class Meta:
        model = Blog
        fields = "__all__"


class BlogCreateSerializer(serializers.ModelSerializer):
    """Blog create serializer"""

    class Meta:
        model = Blog
        fields = ["blog_name", "blog_intro"]

    # def get_blog_subscriptions_count(self, obj):
    #     subscription_count = Subscription.objects.filter(article=obj).count()
    #     return subscription_count


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""

    class Meta:
        model = Category
        fields = "__all__"


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Category serializer"""

    class Meta:
        model = Category
        fields = ["ctg_name"]


class ArticleSerializer(serializers.ModelSerializer):
    """Article serializer"""

    class Meta:
        model = Article
        fields = "__all__"

    def get_article_likes_count(self, obj):
        article_likes = Like.objects.filter(article=obj).count()
        return article_likes


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Article create serializer"""

    class Meta:
        model = Article
        fields = ["title", "content", "image"]


class CommentSerializer(serializers.ModelSerializer):
    """Comment Serializer"""

    class Meta:
        model = Comment
        fields = ["user", "comment", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["comment"]
