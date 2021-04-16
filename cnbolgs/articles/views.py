from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, \
    CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import Article, ArticleTag, ArticleComment, ArtileUpDown
from .serializers import TagSerializer, CategorySerializer, ArticleSerializer, ArticleTagSerializer, \
    ArticleCommentSerializer, ArtileUpDownSerializer


class TagView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin,
              GenericViewSet):
    """文章标签增删改查"""

    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return self.request.user.tag_set.all()


class CategoryView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin,
                   GenericViewSet):
    """文章种类增删改查"""

    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return self.request.user.category_set.all()


class ArticleView(ListModelMixin, RetrieveModelMixin,
                  GenericViewSet):
    """文章查"""

    queryset = Article.objects.filter(status=2).order_by('id')
    serializer_class = ArticleSerializer


class ArticleLoggerView(CreateModelMixin, UpdateModelMixin,
                        GenericViewSet):
    """文章增加/修改"""

    permission_classes = [IsAuthenticated]
    serializer_class = ArticleSerializer


class ArticleTagView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin,
                     GenericViewSet):
    """文章标签中间表"""

    permission_classes = [IsAuthenticated]
    queryset = ArticleTag.objects.all()
    serializer_class = ArticleTagSerializer


class ArticleCommentView(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    """文章评论查/新增"""

    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCommentSerializer

    def get_queryset(self):
        article = self.request.article
        return ArticleComment.objects.filter(is_delete=0, article=article).order_by('-create_time').order_by('id')


class ArticleCommentUpdateDestoryView(UpdateModelMixin,
                                      GenericViewSet):
    """文章评论修改/删除"""

    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCommentSerializer

    def get_queryset(self):
        user = self.request.user
        article = self.request.article
        return ArticleComment.objects.filter(user=user, article=article).order_by('id')


class ArtileUpDownView(ListModelMixin, RetrieveModelMixin, CreateModelMixin,
                       GenericViewSet):
    """文章点赞/反对"""

    serializer_class = ArtileUpDownSerializer

    def get_queryset(self):
        user = self.request.user
        article = self.request.article
        return ArtileUpDown.objects.filter(user=user, article=article).order_by('id')
