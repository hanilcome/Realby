from django.db import models
from users.models import User
from ckeditor.fields import RichTextField
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator


class Blog(models.Model):
    """블로그"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="블로거")
    alphanumeric = RegexValidator(r'^[a-zA-Z]*$', '오직 영문자/숫자 만 허용 됩니다.')
    blog_name = models.CharField(max_length=30, validators=[MinLengthValidator(1), alphanumeric], unique=True)
    blog_title = models.CharField(max_length=30, unique=True)
    blog_intro = models.TextField(blank=True, null=True)
    hits = models.PositiveIntegerField(default=0, verbose_name="방문자수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="개설일")
    subscribes = models.ManyToManyField(
        "self", symmetrical=False, related_name="my_subscribers", blank=True
    )

    def __str__(self):
        return self.blog_name


class BlogHits(models.Model):
    client_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, verbose_name="사용자 IP주소"
    )
    date = models.DateField(auto_now_add=True, verbose_name="조회 날짜")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.blog.id)

class Category(models.Model):
    """유저가 직접 지정하는 카테고리"""

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=30,
        verbose_name="카테고리",
    )

    def __str__(self):
        return self.category


class Article(models.Model):
    class TopicChoices(models.TextChoices):
        LIFE = "LIFE", "일상"
        TRAVEL = "TRAVEL", "여행, 맛집"
        CULTURE = "CULTURE", "문화"
        IT = "IT", "IT"
        SPORTS = "SPORTS", "스포츠"

    """게시글"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="blogs")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="카테고리",
    )
    topic = models.CharField(
        max_length=20,
        choices=TopicChoices.choices,
        blank=True,
        verbose_name="토픽",
    )
    title = models.CharField(max_length=50, verbose_name="제목")  # 제목은그대로 두고
    content = RichTextField(verbose_name="내용")  # 내용에서 웹에디터 사용으로 필드가 변경됨(이미지와 텍스트필드 삭제)
    hits = models.PositiveIntegerField(default=0, verbose_name="조회수")
    empathys = models.PositiveIntegerField(default=0, verbose_name="공감수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.title


class ArticleEmpathys(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="empathy_user"
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="empathy_article"
    )


class ArticleHits(models.Model):
    client_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, verbose_name="사용자 IP주소"
    )
    date = models.DateField(auto_now_add=True, verbose_name="조회 날짜")
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.article.id)


class Comment(models.Model):
    """댓글"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments", verbose_name="게시글"
    )
    comment = models.TextField(null=False, verbose_name="댓글")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return self.comment


class ReComment(models.Model):
    """대댓글"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="recomments"
    )
    recomment = models.TextField(null=False, verbose_name="대댓글")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return self.recomment
