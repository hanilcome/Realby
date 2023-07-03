from django.db import models
from users.models import User
from blogs.models import Blog


class BlogMessage(models.Model):
    user = models.ForeignKey(User, related_name='blog_messages', on_delete=models.CASCADE)
    chat = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    blog_room = models.ForeignKey(Blog, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
    

class BlogRoom(models.Model):
    is_active = models.BooleanField(default=False)
    room = models.ForeignKey(Blog, related_name='blog_room_id', on_delete=models.CASCADE)
    
class UserMessage(models.Model):
    user_room1 = models.ForeignKey(User, related_name='user_room_me', on_delete=models.CASCADE)
    user_room2 = models.ForeignKey(User, related_name='user_room_youme', on_delete=models.CASCADE)
    chat = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

    def last_30_messages(self):
        """가장 최신의 30개의 메세지만 로드되도록 하는 함수"""
        return UserMessage.objects.order_by('-created_at').all()[::-1]

    
