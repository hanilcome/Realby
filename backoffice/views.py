from django.db.models import Q
from blogs.models import *
from users.models import User
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
import threading
from backoffice.serializers import BackArticleSerializer


class BackArticleHitView(APIView):

    def get(self, request, blog_name):
        """블로그 전체게시글"""
        blog = Blog.objects.filter(blog_name=blog_name)
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-hits", "-created_at")[0:5]
        serializer = BackArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BackArticleEmpathyView(APIView):

    def get(self, request, blog_name):
        """블로그 전체게시글"""
        blog = Blog.objects.filter(blog_name=blog_name)
        print("1")
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-empathys", "-created_at")[0:5]
        print("2")
        serializer = BackArticleSerializer(articles, many=True)
        print("3")
        return Response(serializer.data, status=status.HTTP_200_OK)