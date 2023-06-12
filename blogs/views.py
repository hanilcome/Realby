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
        """카테고리 생성"""
        serializers = CategoryCreateSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save(blog_id=blog_id)
            return Response({"message": "카테고리 생성 완료"}, status=status.HTTP_201_CREATED)
        elif Category.objects.filter().exists():
            return Response(
                {"message": "이미 존재하는 카테고리입니다"}, status=status.HTTP_400_BAD_REQUEST
            )


class BlogCreateView(APIView):
    def post(self, request):
        """블로그 개설"""

        serializer = BlogCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "블로그 개설완료"}, status=status.HTTP_201_CREATED)
        elif Blog.objects.filter().exists():
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


class ArticleView(APIView):
    """게시글"""

    def get(self, request, article_id):
        """상세게시글 불러오기"""
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """게시글 작성"""
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
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
        article = get_object_or_404(Article, id=article_id)
        try:
            articlelikes = Like.objects.get(article=article, user=request.user)
            articlelikes.delete()
            return Response({"message": "좋아요를 취소했습니다"}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            articlelikes = Like.objects.create(article=article, user=request.user)
            return Response({"message": "좋아요를 눌렀습니다"}, status=status.HTTP_200_OK)


class CommentView(APIView):
    """댓글"""

    def get(self, request, article_id):
        """댓글 불러오기"""
        article = Article.objects.get(id=article_id)
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        """댓글 작성"""
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user, article=Article.objects.get(pk=article_id)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, comment_id):
        """댓글 수정"""
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            serializer = CommentDetailSerializer(
                comment, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("수정 권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response("삭제 완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("수정 권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)
