from django.db import models
from users.models import User

class ChatList(models.Model):
    
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    chat = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
