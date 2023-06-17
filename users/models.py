from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("이메일을 입력하세요")
        if not username:
            raise ValueError("닉네임을 입력하세요")  # email, username을 필수값으로 지정
        user = self.model(
            username=username,
            email=self.normalize_email(email),  # email 정규화한 후,
        )  # 유저 생성

        user.set_password(password)  # 생성된 유저의 password는 set_password 메서드로 해시화하여 안전하게 저장
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            username,
            password=password,
        )  # 일반 유저를 생성한 후,
        user.is_admin = True  # 해당 유저를 관리자로 설정
        user.is_active = 1  # superuser가 이메일 인증 안하게!
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField("이메일", max_length=255, unique=True)
    username = models.CharField("닉네임", max_length=50, unique=True)
    birthdate = models.DateField(
        "생년월일",
        validators=[MinValueValidator(date(1900, 1, 1)), MaxValueValidator(date.today)],
        null=True,
        blank=True,
    )
    profile_img = models.ImageField("프로필 이미지", null=True, blank=True, upload_to="%Y/%m")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"  # 사용자 모델 고유식별자로 email 필드 지정
    REQUIRED_FIELDS = [
        "username",
    ]  # 필수로 입력받을 필드 지정

    def __str__(self):
        return self.email

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
