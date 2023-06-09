from django.shortcuts import render
from blogs.models import *
from blogs.serializers import *
from users.models import User
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404


# Create your views here.
class BlogView(APIView):
    """블로그 전체"""

    def get(self, request, blog_id):
        """블로그정보 불러오기"""
        blog = get_object_or_404(Blog, id=blog_id)
        serializer = BlogSerializer(blog)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, blog_id):
        """블로그 개설"""
        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, id=blog_id)
            return Response({"message": "블로그 개설완료"}, status=status.HTTP_201_CREATED)
        elif Blog.objects.filter(blog_name=request.blog_name).exists():
            return Response(
                {"message": "이미 존재하는 블로그입니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"message": "블로그 이름을 입력해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )


class CategoryView(APIView):
    """카테고리"""

    article_serializer = ArticleSerializer

    def get(self, request, category_id):
        """카테고리별 게시글 불러오기"""

        category_articles = Article.objects.filter(id=category_id)
        serializer = self.article_serializer(category_articles, many=True)
        return Response(serializer.data)

    def post(self, request, blog_id):
        """카테고리 생성"""
        serializers = CategorySerializer(data=request.data)
        if serializers.is_valid():
            serializers.save(user=request.user, id=blog_id)
            return Response({"message": "카테고리 생성 완료"}, status=status.HTTP_201_CREATED)
        elif Category.objects.filter(ctg_name=request.ctg_name).exists():
            return Response(
                {"message": "이미 존재하는 카테고리입니다"}, status=status.HTTP_400_BAD_REQUEST
            )


class ArticleView(APIView):
    """게시글"""

    def get(self, request, article_id):
        """상세게시글 불러오기"""
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, category_id):
        """게시글 작성"""
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, category_id=category_id)
            return Response({"message": "게시글 작성 완료"}, status=status.HTTP_201_CREATED)

    def put(self, request, article_id):
        """게시글 수정"""
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleSerializer(
                article,
                data=request.data,
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        """게시글 삭제"""
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            article.delete()
            return Response("삭제완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class ArticleLikeView(APIView):
    """게시글 공감"""

    def post(self, request, article_id):
        """게시글 공감누르기"""
        pass

    pass


class CommentView(APIView):
    """댓글"""

    def get(self, request, comment_id):
        """댓글 불러오기"""
        pass

    def post(self, request, article_id):
        """댓글 작성"""
        pass

    def put(self, request, comment_id):
        """댓글 수정"""
        pass

    def delete(self, request, comment_id):
        """댓글 삭제"""
        pass

    pass
