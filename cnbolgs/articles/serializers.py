from rest_framework import serializers

from .models import Tag, Category


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
