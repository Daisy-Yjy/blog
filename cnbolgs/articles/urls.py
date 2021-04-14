from django.urls import path, re_path

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
]