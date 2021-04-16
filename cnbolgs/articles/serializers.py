from rest_framework import serializers

from .models import Tag, Category, Article, ArticleTag, ArticleComment, ArtileUpDown


class TagSerializer(serializers.ModelSerializer):
    """文章标签序列化器"""

    class Meta:
        model = Tag
        fields = ['user', 'title']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        tag = Tag.objects.create(**validated_data)
        return tag


class CategorySerializer(serializers.ModelSerializer):
    """文章种类序列化器"""

    class Meta:
        model = Category
        fields = ['user', 'title', 'desc', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        category = Category.objects.create(**validated_data)
        return category


class ArticleSerializer(serializers.ModelSerializer):
    """文章序列化器"""

    class Meta:
        model = Article
        fields = "__all__"


class ArticleTagSerializer(serializers.ModelSerializer):
    """文章标签中间表"""

    class Meta:
        model = ArticleTag
        fields = "__all__"


class ArticleCommentSerializer(serializers.ModelSerializer):
    """文章评论"""

    is_delete = serializers.BooleanField(default=False, label='是否删除', write_only=True)

    class Meta:
        model = ArticleComment
        fields = '__all__'

    def create(self, validated_data):
        article = validated_data.get('article')
        comment = ArticleComment.objects.create(**validated_data)
        article.comment_count += 1
        article.save()
        return comment

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        try:
            instance.is_delete = validated_data.get('is_delete', instance.is_delete)
            article = instance.article
            article.comment_count -= 1
            article.save()
        except:
            pass
        instance.save()
        return instance


class ArtileUpDownSerializer(serializers.ModelSerializer):
    """文章点赞、反对"""

    class Meta:
        model = ArtileUpDown
        fields = "__all__"

    def create(self, validated_data):
        article = validated_data.get('article')
        up_down = ArtileUpDown.objects.create(**validated_data)
        if validated_data.get('is_up') == 1:
            article.up_count += 1
            article.save()
        if validated_data.get('is_up') == 2:
            article.up_count -= 1
            article.save()
        return up_down
