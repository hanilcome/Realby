from django.shortcuts import render
from blogs.models import *
from blogs.serializers import *
from users.models import User
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
import threading


class MainView(APIView):
    def get(self, request):
        """메인피드 불러오기"""
        articles = Article.objects.all().order_by("-hits")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BlogView(APIView):
    """블로그 전체"""

    def get(self, request, blog_name):
        """블로그정보 불러오기"""
        blog = get_object_or_404(Blog, blog_name=blog_name)
        serializer = BlogSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, blog_name):
        """카테고리 생성"""
        serializers = CategoryCreateSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save(blog_name=blog_name)
            return Response({"message": "카테고리 생성 완료"}, status=status.HTTP_201_CREATED)
        elif Category.objects.filter().exists():
            return Response(
                {"message": "이미 존재하는 카테고리입니다"}, status=status.HTTP_400_BAD_REQUEST
            )


class BlogCreateView(APIView):
    def post(self, request):
        """블로그 개설"""
        blog = Blog.objects.filter()
        serializer = BlogCreateSerializer(data=request.data)
        
        a=0
        for n in range(len(blog)):
            if blog[n].user_id == request.user.id:
                a += 1
                
        if serializer.is_valid():
            if a == 0: 
                serializer.save(user=request.user)
                return Response({"message": "블로그 개설완료"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "이미 개설된 블로그가 존재합니다!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)

class SubscribeView(APIView):
    """구독한 특정 유저의 이름, 아이디 목록을 반환"""
    def get(self, request, blog_name):
        blog = get_object_or_404(Blog, blog_name=blog_name)
        serializer = BlogSubscribeSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """특정 유저를 구독함"""
    def post(self, request, blog_name):
        blog = get_object_or_404(Blog, blog_name=blog_name)
        you = get_object_or_404(Blog, id=blog.id)
        me = request.user
        if me != you:
            if me in you.my_subscribers.all():
                you.my_subscribers.remove(me)
                return Response("구독 취소", status=status.HTTP_204_NO_CONTENT)
            else:
                you.my_subscribers.add(me)
                return Response("구독", status=status.HTTP_200_OK)
        else:
            return Response(
                "자기 자신은 구독 할 수 없습니다!", status=status.HTTP_205_RESET_CONTENT
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
    """블로그 전체게시글"""
    def get(self, request, blog_name):
        blog = Blog.objects.filter(blog_name=blog_name)
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-hits")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    """게시글 작성"""
    def post(self, request, blog_name):
        blog = Blog.objects.filter(blog_name=blog_name)
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, blog_id=blog[0].id)
            return Response({"message": "게시글 작성 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

class ArticleDetailView(APIView):
    """일정 시간 지나면 ip 자동 삭제하는 함수"""
    def timer_delete(article_id, hit):
        articlehit = ArticleHits.objects.filter(article_id=article_id, client_ip=hit)
        print(articlehit)
        articlehit.delete()
        
    """상세게시글 불러오기"""
    def get(self, request, blog_name, article_id):
        blog = Blog.objects.filter(blog_name=blog_name)
        article = get_object_or_404(Article, blog_id=blog[0].id, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """조회수 기능(ip기반)"""
    def post(self, request, blog_name, article_id):
        blog = Blog.objects.filter(blog_name=blog_name)
        article = get_object_or_404(Article, blog_id=blog[0].id, id=article_id)
        hit = ArticleHitSerializer.get_client_ip(request)
        articlehit = ArticleHits.objects.filter(article_id=article_id).values()
        serializer = ArticleHitSerializer(data=request.data)
        
        a = 0
        for n in range(len(articlehit)):
            if hit == articlehit[n]['client_ip']:
                a += 1
                
        if bool(articlehit) is False or a == 0:
            if serializer.is_valid():
                    article.hits += 1
                    article.save()
                    serializer.save(client_ip=hit ,article_id=article_id, blog_id=blog[0].id)
                    threading.Timer(20, ArticleDetailView.timer_delete, args=(article_id, hit)).start()
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response("동일한 ip주소가 존재합니다.", status=status.HTTP_205_RESET_CONTENT)
    
    def put(self, request, blog_name, article_id):
        """게시글 수정"""
        blog = Blog.objects.filter(blog_name=blog_name)
        article = get_object_or_404(Article, blog_id=blog[0].id, id=article_id)
        if request.user == article.user:
            serializer = ArticleCreateSerializer(
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

    def delete(self, request, blog_name, article_id):
        """게시글 삭제"""
        blog = Blog.objects.filter(blog_name=blog_name)
        article = get_object_or_404(Article,  blog_id=blog[0].id, id=article_id)
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


