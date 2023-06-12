from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class UserManager(BaseUserManager):
    def create_user(self, email, username, age, password=None):
        if not email:
            raise ValueError("이메일을 입력하세요")
        if not username:
            raise ValueError("닉네임을 입력하세요")
        user = self.model(
            username=username,
            age=age,
            email=self.normalize_email(email), 
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, age, password=None):
        user = self.create_user(
            email,
            username,
            age=age,
            password=password,
        )
        user.is_admin = True
        # superuser가 이메일 인증 안하게!
        user.is_active = 1
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField("이메일", max_length=255, unique=True)
    username = models.CharField("닉네임", max_length=50, default="사용자", unique=True)
    age = models.IntegerField("나이", validators=[MinValueValidator(7), MaxValueValidator(100)])
    profile_img = models.ImageField("프로필 이미지", null=True, blank=True, upload_to="%Y/%m")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    subscribes = models.ManyToManyField("self", symmetrical=False, related_name="my_subscribers", blank=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username","age",]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

