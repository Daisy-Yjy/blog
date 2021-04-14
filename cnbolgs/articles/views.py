from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, \
    CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .serializers import TagSerializer, CategorySerializer


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

