from django.db import models

from users.models import User


class Tag(models.Model):
    """文章标签"""

    title = models.CharField(max_length=15, verbose_name='标签标题')
    desc = models.CharField(max_length=50, verbose_name='标签描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        db_table = 'tb_tag'
        verbose_name = '文章标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Category(models.Model):
    """文章分类"""

    CATEGORY_STATUS_CHOICES = (
        (1, '可见'),
        (0, '不可见')
    )
    title = models.CharField(max_length=15, verbose_name='分类标题')
    desc = models.CharField(max_length=50, verbose_name='分类描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    status = models.PositiveSmallIntegerField(choices=CATEGORY_STATUS_CHOICES, default=1, verbose_name='分类'
                                                                                                       '状态')

    class Meta:
        db_table = 'tb_category'
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Article(models.Model):
    """文章"""

    ARTICLE_STATUS_CHOICES = (
        (1, "草稿"),
        (2, "已发布"),
        (3, "已删除"),
        (4, "已封禁"),
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    title = models.CharField(max_length=100, verbose_name='文章标题', db_index=True)
    content = models.TextField(verbose_name='文章内容', null=True, blank=True)
    views = models.PositiveIntegerField(default=0, verbose_name='浏览量')
    status = models.PositiveSmallIntegerField(choices=ARTICLE_STATUS_CHOICES, default=1, verbose_name='文章状态')
    comment_count = models.IntegerField(default=0, verbose_name='评论数')
    up_count = models.IntegerField(default=0, verbose_name='点赞数')
    down_count = models.IntegerField(default=0, verbose_name='反对数')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='分类', null=True)
    tags = models.ManyToManyField(Tag, through='ArticleTag', through_fields=('article', 'tag'),
                                  verbose_name='标签')

    class Meta:
        db_table = 'tb_article'
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ArticleTag(models.Model):
    """文章标签中间表"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='文章')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='标签')

    class Meta:
        db_table = 'tb_article_tag'
        verbose_name = '文章标签中间表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s-%s" % (self.article.title, self.tag.title)


class ArticleComment(models.Model):
    """文章评论"""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='文章')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户')
    content = models.CharField(max_length=1000, verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'tb_article_comment'
        verbose_name = '文章评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content


class ArtileUpDown(models.Model):
    """点赞/反对表"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='文章')
    ups = models.TextField(default=',')

    class Meta:
        db_table = 'tb_article_up_down'
        verbose_name = '文章点赞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s-%s" % (self.article.title, self.user.username)
