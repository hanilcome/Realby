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
            
    def delete(self, request, blog_name):
        """블로그 삭제"""        
        
        blog = get_object_or_404(Blog, blog_name=blog_name)
        if request.user.id == blog.user_id:
            blog.delete()
            return Response("삭제완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


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
    
    def get(self, request, blog_name):
        """구독한 특정 유저의 이름, 아이디 목록을 반환"""
        
        blog = get_object_or_404(Blog, blog_name=blog_name)
        serializer = BlogSubscribeSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, blog_name):
        """특정 블로그를 구독함"""
        
        blog = get_object_or_404(Blog, blog_name=blog_name)
        me = request.user.id
        if me != blog.user_id:
            try:
                if me != blog.my_subscribers.filter(user_id=me)[0].user_id:
                    blog.my_subscribers.add(me)
                    return Response("구독", status=status.HTTP_200_OK)
                else:
                    blog.my_subscribers.remove(me)
                    return Response("구독 취소", status=status.HTTP_204_NO_CONTENT)
            except IndexError:
                blog.my_subscribers.add(me)
                return Response("구독", status=status.HTTP_200_OK)
        else:
            return Response(
                "자기 자신은 구독 할 수 없습니다!", status=status.HTTP_205_RESET_CONTENT
            )
            

class CategoryView(APIView):

    def get(self, request, blog_name):
        """블로그 카테고리 목록 불러오기"""

        blog = Blog.objects.filter(blog_name=blog_name)
        category_articles = Category.objects.filter(blog_id=blog[0].id)
        serializer = CategorySerializer(category_articles, many=True)
        return Response(serializer.data)
    
    def post(self, request, blog_name):
        """카테고리 생성"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        serializer = CategoryCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(blog_id=blog[0].id)
            return Response({"message": "카테고리 생성 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)
        
    def delete(self, request, blog_name, category_id):
        """카테고리 삭제"""
        
        blog = get_object_or_404(Blog, blog_name=blog_name)
        category = get_object_or_404(Category, id=category_id)
        if request.user.id == blog.user_id:
            category.delete()
            return Response("삭제완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    


class ArticleView(APIView):
    def get(self, request, blog_name):
        """블로그 전체게시글"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-hits")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, blog_name):
        """게시글 작성"""
        
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
    def timer_delete(article_id, hit):
        """일정 시간 지나면 ip 자동 삭제하는 함수"""
    
        articlehit = ArticleHits.objects.filter(article_id=article_id, client_ip=hit)
        print(articlehit)
        articlehit.delete()
        
    def get(self, request, blog_name, article_id):
        """상세게시글 불러오기"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        article = get_object_or_404(Article, blog_id=blog[0].id, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, blog_name, article_id):
        """조회수 기능(ip기반)"""
        
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
        """댓글 삭제"""
        
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response("삭제 완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("수정 권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

class ReCommentView(APIView):
    
    def post(self, request, article_id, comment_id):
        """대댓글 작성"""
        
        serializer = ReCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user, article=Article.objects.get(pk=article_id), comment=Comment.objects.get(pk=comment_id)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
