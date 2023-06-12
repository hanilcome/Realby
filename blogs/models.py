from django.db import models
from users.models import User


class Blog(models.Model):
    """블로그"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="블로거")
    blog_name = models.CharField(max_length=30, unique=True)
    blog_intro = models.TextField(blank=True, null=True)
    blog_hits = models.PositiveIntegerField(default=0, verbose_name="방문자수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="개설일")

    def __str__(self):
        return self.blog_name


class Category(models.Model):
    """유저가 직접 지정하는 카테고리"""

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name="블로그")
    category = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="카테고리",
    )

    def __str__(self):
        return self.category


class Article(models.Model):
    """게시글"""

    class TopicChoices(models.TextChoices):
        """토픽설정"""

        LIFE = "LIFE", "일상"
        TRAVEL = "TRAVEL", "여행, 맛집"
        CULTURE = "CULTURE", "문화"
        IT = "IT", "IT"
        SPORTS = "SPORTS", "스포츠"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="작성자")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="카테고리",
    )
    topic = models.CharField(
        choices=TopicChoices.choices,
        max_length=30,
        null=True,
        blank=True,
        verbose_name="토픽",
    )
    title = models.CharField(max_length=50, verbose_name="제목")
    content = models.TextField("내용")
    image = models.ImageField(blank=True, null=True)
    hits = models.PositiveIntegerField(default=0, verbose_name="조회수")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.title


class ArticleHits(models.Model):
    client_ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, null=True, verbose_name='사용자 IP주소')
    date = models.DateField(auto_now_add=True, verbose_name='조회 날짜')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="ipaddress")

    def __str__(self):
        return str(self.article.id)
    

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
