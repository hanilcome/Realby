from django.db import models
from users.models import User


# Create your models here.


class Topic(models.Model):
    """운영자가 지정한 토픽"""

    topic_name = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.topic_name


class Blog(models.Model):
    """블로그"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="블로거")
    blog_name = models.CharField(max_length=30, null=False, unique=True)
    blog_intro = models.TextField(blank=True, null=True)
    blog_hits = models.PositiveIntegerField(default=0, verbose_name="방문자수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="개설일")

    def __str__(self):
        return self.blog_name


class Category(models.Model):
    """유저가 직접 지정하는 카테고리"""

    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name="블로그")
    ctg_name = models.CharField(
        max_length=30, null=True, blank=True, unique=True, verbose_name="카테고리"
    )

    def __str__(self):
        return self.ctg_name


class Article(models.Model):
    """게시글"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    blog_id = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name="블로그")
    category_id = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="카테고리"
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name="토픽")
    title = models.CharField(max_length=50, default="제목없음", verbose_name="제목")
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    article_hits = models.PositiveIntegerField(default=0, verbose_name="조회수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.title


class Comment(models.Model):
    """댓글"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="게시글")
    comment = models.TextField(null=False, verbose_name="댓글")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return self.comment


class Like(models.Model):
    """공감"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="게시글")
