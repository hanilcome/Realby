from django.contrib import admin
from blogs.models import *

# Register your models here.

admin.site.register(Blog)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Comment)
