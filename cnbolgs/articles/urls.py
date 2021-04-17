from django.urls import path

from . import views

urlpatterns = [
    # 标签查所有/新增
    path('tags/', views.TagView.as_view({'get': 'list', 'post': 'create'})),
    # 标签查单一/修改/删除
    path('tags/<int:pk>/', views.TagView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    # 种类查所有/新增
    path('categorys/', views.CategoryView.as_view({'get': 'list', 'post': 'create'})),
    # 种类查单一/修改/删除
    path('categorys/<int:pk>/', views.CategoryView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    # 文章 用户查所有
    path('articles/', views.ArticleView.as_view({'get': 'list'})),
    # 文章 用户查单一
    path('articles/<int:pk>/', views.ArticleView.as_view({'get': 'retrieve'})),
    # 文章 博主新增
    path('article/', views.ArticleLoggerView.as_view({'post': 'create'})),
    # 文章 博主修改
    path('article/<int:pk>/', views.ArticleLoggerView.as_view({'put': 'update'})),
    # 标签中间表 增删改查
    path('articles_tags/', views.ArticleTagView.as_view({'get': 'list', 'post': 'create'})),
    path('articles_tags/<int:pk>/', views.ArticleTagView.as_view({'put': 'update', 'delete': 'destroy'})),
    # 评论 查所有 单一
    path('articles_comments/', views.ArticleCommentView.as_view({'get': 'list', 'post': 'create'})),
    path('articles_comments/<int:pk>/', views.ArticleCommentView.as_view({'get': 'retrieve'})),
    # 评论 用户自己修改
    path('articles_comment/<int:pk>/', views.ArticleCommentUpdateDestoryView.as_view({'put': 'update'})),
    # 文章点赞、反对
    path('articles_up_down/', views.ArtileUpDownView.as_view({'get': 'list', 'post': 'create'})),
    path('articles_up_down/<int:pk>/', views.ArtileUpDownView.as_view({'get': 'retrieve'})),
]