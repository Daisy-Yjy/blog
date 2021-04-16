from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=True, verbose_name='邮箱激活状态')
    # create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 待迁移
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png')
    blogger = models.BooleanField(default=False)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class GithubUser(models.Model):
    """github登录用户数据"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    openid = models.CharField(max_length=64, verbose_name="openid", db_index=True)
    # create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = "tb_oauth_github"
        verbose_name = "Github登录用户数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


