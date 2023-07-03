from django.urls import path
from backoffice import views

urlpatterns = [
    path(
    "<str:blog_name>/hits/",
    views.BackArticleHitView.as_view(),
    name="backarticle_hit_view",
    ),
    path(
    "<str:blog_name>/empathys/",
    views.BackArticleEmpathyView.as_view(),
    name="backarticle_empathy_view",
    ),
]