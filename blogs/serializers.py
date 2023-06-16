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
        fields = ("category",)


class ArticleSerializer(serializers.ModelSerializer):
    blog = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    
    def get_blog(self, obj):
        return obj.blog.blog_name
    
    
    def get_category(self, obj):
        if obj.category:
            return obj.category.category
        else:
            pass
        
    
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
        fields = ("title", "content", "category", "topic")


class ReCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ("id","user","recomment","created_at")


class CommentSerializer(serializers.ModelSerializer):
    recomments = ReCommentSerializer(many=True)

    
    """Comment Serializer"""

    class Meta:
        model = Comment
        fields = ("id","user", "comment", "created_at", "article", "recomments")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("comment",)
        

class CommentDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("comment",)
        

class ReCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReComment
        fields = ("recomment",)


class ArticleEmpathySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ArticleEmpathys
        fields = ""


class ArticleHitSerializer(serializers.ModelSerializer):
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    class Meta:
        model = ArticleHits
        fields = ""

class BlogSubscribeSerializer(serializers.ModelSerializer):
    subscribes = serializers.StringRelatedField(many=True)
    my_subscribers = serializers.StringRelatedField(many=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "blog_name",
            "my_subscribers",
            "subscribes"
        )

