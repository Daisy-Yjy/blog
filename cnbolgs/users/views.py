import random
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import RegisterViewSerializer
from libs.yuntongxun import sms


class UsernameCountView(APIView):
    """判断用户名是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {'username': username, 'count': count}
        return Response(data)


class MobileCountView(APIView):
    """判断手机号是否存在"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {'mobile': mobile, 'count': count}
        return Response(data)


class RegisterView(CreateAPIView):
    """用户注册"""
    serializer_class = RegisterViewSerializer


class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get('sms_%s' % mobile)
        if send_flag:
            return Response({'message': '短信验证码发送频繁'}, status=status.HTTP_400_BAD_REQUEST)
        sms_codes = '%06d' % random.randint(0, 999999)
        # 发送验证码
        sms.CCP().send_template_sms(mobile, [sms_codes, 5], 1)

        redis_conn.setex('sms_%s' % mobile, 300, sms_codes)
        redis_conn.setex('send_flag_%s' % mobile, 60, sms_codes)

        return Response({'message': 'OK'})
