from django.contrib import admin

from .models import Category, Tag, Article, ArticleTag, ArticleComment, ArtileUpDown


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(ArticleTag)
admin.site.register(ArticleComment)
admin.site.register(ArtileUpDown)
