from django.urls import path
from blogs import views

urlpatterns = [
    path( 
        "",
        views.MainView.as_view(),
        name="mainview",
    ),
    path( 
        "blogcreate/",
        views.BlogCreateView.as_view(),
        name="blogcreateview",
    ),
    path(
        "<int:blog_id>/",
        views.BlogView.as_view(),
        name="blogview",
    ),
    # path(
    #     "<int:blog_id>/category/<int:category_id>/",
    #     views.CategoryView.as_view(),
    #     name="categoryview",
    # ),
    path(
        "write/",
        views.ArticleView.as_view(),
        name="articlecreateview",
    ),
    path(
        "<int:blog_id>/detail/",
        views.ArticleView.as_view(),
        name="articleview",
    ),
    path(
        "<int:blog_id>/<int:article_id>/",
        views.ArticleDetailView.as_view(),
        name="articledetailview",
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
        "comments/<int:comment_id>/",
        views.CommentView.as_view(),
        name="commentview",
    ),
    path(
        "subscribe/<int:blog_id>/", 
        views.SubscribeView.as_view(),
        name="user_subscribe_view"
    ),
]
