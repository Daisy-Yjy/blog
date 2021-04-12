import re
from django.contrib.auth.backends import ModelBackend

from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """重写返回数据"""
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }


def get_user_by_account(username):
    """
    通过传入的账号，获取user 模型对象
    :param username: 邮箱或用户名
    :return: user 或 None
    """
    try:
        if re.match(r'[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', username):
            user = User.objects.get(email=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    return user


class UsernameEmailAuthBackend(ModelBackend):
    """修改django的认证类，为了实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取到User
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user



