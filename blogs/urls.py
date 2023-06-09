from django.urls import path
from blogs import views

urlpatterns = [
    path(
        "",
        views.BlogView.as_view(),
        name="blogview",
    ),
    path(
        "<int:blog_id>/",
        views.BlogView.as_view(),
        name="blogview",
    ),
    path(
        "<int:blog_id>/<int:category_id>/",
        views.CategoryView.as_view(),
        name="categoryview",
    ),
    path(
        "<int:blog_id>/write/",
        views.ArticleView.as_view(),
        name="articleview",
    ),
    path(
        "<int:blog_id>/<int:article_id>/",
        views.ArticleView.as_view(),
        name="articleview",
    ),
    path(
        "<int:article_id>/like/",
        views.ArticleLikeView.as_view(),
        name="articlelikeview",
    ),
    path(
        "<int:article_id>/comments/",
        views.CommentView.as_view(),
        name="commentview",
    ),
    path(
        "<int:article_id>/<int:comment_id>/",
        views.CommentView.as_view(),
        name="commentview",
    ),
]
