from django.db.models import Q
from blogs.models import *
from blogs.serializers import *
from users.models import User
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
import threading
from rest_framework.pagination import PageNumberPagination
from .pagination import PaginationManage


class ArticlePagination(PageNumberPagination):
    """페이지네이션 페이지 수"""

    page_size = 100


class MainView(APIView):
    def get(self, request):
        """메인피드 불러오기"""

        articles = Article.objects.all().order_by("-hits")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogView(APIView):
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
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """블로그 개설"""

        blog = Blog.objects.filter()
        serializer = BlogCreateSerializer(data=request.data)

        if not request.user.is_authenticated:
            return Response({"message": "로그인 해주세요"}, 401)

        a = 0
        for n in range(len(blog)):
            if blog[n].user_id == request.user.id:
                a += 1

        if serializer.is_valid():
            if a == 0:
                serializer.save(user=request.user)
                return Response({"message": "블로그 개설완료"}, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "이미 개설된 블로그가 존재합니다!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogList(APIView):
    def get(self, request, user_id):
        """블로그 리스트 가져오기"""
        blog = Blog.objects.filter(user_id=user_id)
        serializer = BlogSerializer(blog, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        subscribes = Blog.objects.filter(user_id=me)[0]

        if subscribes != blog:
            if subscribes in blog.my_subscribers.all():
                blog.my_subscribers.remove(subscribes)
                return Response("구독 취소", status=status.HTTP_204_NO_CONTENT)
            else:
                blog.my_subscribers.add(subscribes)
                return Response("구독", status=status.HTTP_200_OK)
        else:
            return Response("자기 자신은 구독 할 수 없습니다!", status=status.HTTP_205_RESET_CONTENT)


class CategoryView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

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


class ArticleView(APIView, PaginationManage):
    pagination_class = ArticlePagination

    def get(self, request, blog_name):
        """블로그 전체게시글"""
        blog = Blog.objects.filter(blog_name=blog_name)
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-created_at")
        # page = self.paginate_queryset(articles)

        # if page is not None:
        #     serializer = self.get_paginated_response(
        #         ArticleSerializer(page, many=True).data
        #     )
        # else:
        #     serializer = ArticleSerializer(articles, many=True)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, blog_name):
        """게시글 작성"""

        blog = Blog.objects.filter(blog_name=blog_name)
        serializer = ArticleCreateSerializer(data=request.data)

        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인 해주세요"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if serializer.is_valid():
            serializer.save(user=request.user, blog_id=blog[0].id)
            return Response({"message": "게시글 작성 완료"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    def timer_delete(article_id, hit):
        """일정 시간 지나면 ip 자동 삭제하는 함수"""

        articlehit = ArticleHits.objects.filter(article_id=article_id, client_ip=hit)
        articlehit.delete()

    def get(self, request, article_id):
        """상세게시글 불러오기"""

        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        """조회수 기능(ip기반)"""

        article = get_object_or_404(Article, id=article_id)
        hit = ArticleHitSerializer.get_client_ip(request)
        articlehit = ArticleHits.objects.filter(article_id=article_id).values()
        serializer = ArticleHitSerializer(data=request.data)

        if bool(articlehit) is False and request.user.is_authenticated:
            if serializer.is_valid():
                article.hits += 1
                article.save()
                serializer.save(client_ip=hit, article_id=article_id)
                threading.Timer(
                    20, ArticleDetailView.timer_delete, args=(article_id, hit)
                ).start()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(
                "동일한 ip주소가 존재하거나 로그인이 안되어 있습니다.", status=status.HTTP_205_RESET_CONTENT
            )

    def put(self, request, article_id):
        """게시글 수정"""
        article = get_object_or_404(Article, id=article_id)
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

    def delete(self, request, article_id):
        """게시글 삭제"""

        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            article.delete()
            return Response("삭제완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class ArticleEmpathyView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, article_id):
        """게시글 공감 기능"""

        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleEmpathySerializer(data=request.data)
        article_empathy = ArticleEmpathys.objects.filter(article_id=article_id)

        if bool(article_empathy) is False:
            if serializer.is_valid():
                article.empathys += 1
                article.save()
                serializer.save(article_id=article_id, user_id=request.user.id)
                return Response("공감", status=status.HTTP_200_OK)
        else:
            article.empathys -= 1
            article.save()
            article_empathy.delete()
            return Response("공감 취소", status=status.HTTP_205_RESET_CONTENT)


class CommentView(APIView):
    """댓글"""

    def get(self, request, article_id):
        """해당 게시글의 전체 댓글 불러오기"""

        article = Article.objects.get(id=article_id)
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        """댓글 작성"""

        serializer = CommentCreateSerializer(data=request.data)

        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)

        if serializer.is_valid():
            serializer.save(
                user=request.user, article=Article.objects.get(pk=article_id)
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class CommentDetailView(APIView):
    """댓글상세 설정"""

    def get(self, requst, comment_id):
        """댓글 상세 불러오기"""
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentDetailSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def post(self, request, comment_id):
        """대댓글 작성"""

        serializer = ReCommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                comment=Comment.objects.get(pk=comment_id),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class ReCommentView(APIView):
    """대댓글 관리"""

    def get(self, request, recomment_id):
        """상세 대댓글 불러오기"""
        recomment = get_object_or_404(ReComment, id=recomment_id)
        serializer = ReCommentSerializer(recomment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, recomment_id):
        """대댓글 수정"""
        recomment = get_object_or_404(ReComment, id=recomment_id)
        if request.user == recomment.user:
            serializer = ReCommentCreateSerializer(recomment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("수정 권한이없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, recomment_id):
        """대댓글 삭제"""
        recomment = get_object_or_404(ReComment, id=recomment_id)
        if request.user == recomment.user:
            recomment.delete()
            return Response("삭제 완료", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("수정 권한이없습니다", status=status.HTTP_403_FORBIDDEN)


class SearchView(APIView):
    def get(self, request, blog_name):
        """게시글 검색 기능"""
        blog = Blog.objects.filter(blog_name=blog_name)
        articles = Article.objects.filter(blog_id=blog[0].id).order_by("-created_at")
        search_word = request.GET.get(
            "search-word", ""
        )  # 주소창에 ?search-word='' 형식으로 받아온다.

        if search_word:
            articles = articles.filter(
                Q(title__icontains=search_word) | Q(content__icontains=search_word)
            ).distinct()

        serializer = SearchSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
