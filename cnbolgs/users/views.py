import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import RegisterViewSerializer
from libs.yuntongxun import sms
from cnbolgs import settings


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


class EmailCountView(APIView):
    """判断邮箱是否存在"""

    def get(self, request, email):
        count = User.objects.filter(email=email).count()
        data = {'email': email, 'count': count}
        return Response(data)


class RegisterView(CreateAPIView):
    """用户注册"""
    serializer_class = RegisterViewSerializer


class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        redis_conn = get_redis_connection('sms_codes')
        send_flag = redis_conn.get('sms_%s' % mobile)
        if send_flag:
            return Response({'message': '短信验证码发送频繁'}, status=status.HTTP_400_BAD_REQUEST)
        sms_codes = '%06d' % random.randint(0, 999999)
        # 发送验证码
        sms.CCP().send_template_sms(mobile, [sms_codes, 5], 1)

        redis_conn.setex('sms_%s' % mobile, 300, sms_codes)
        redis_conn.setex('send_flag_%s' % mobile, 60, sms_codes)

        return Response({'message': 'OK'})


class VerifyEmail(APIView):
    """邮箱验证码"""
    def get(self, request, email):
        redis_conn = get_redis_connection('email_codes')
        send_flag = redis_conn.get('email_%s' % email)
        if send_flag:
            return Response({'message': '验证码发送频繁'}, status=status.HTTP_400_BAD_REQUEST)
        email_codes = '%06d' % random.randint(0, 999999)

        redis_conn.setex('email_%s' % email, 300, email_codes)
        redis_conn.setex('send_flag_%s' % email, 60, email_codes)

        subject = "cnblog邮箱验证"  # 邮件主题/标题
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用cnblog。</p>' \
                       '<p>您的邮箱验证码为：%s，请在注册窗口输入该验证码' % email_codes
        # send_mail(subject:标题, message:普通邮件正文, 发件人, [收件人], html_message=超文本的邮件内容)
        send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
        return Response({'message': 'OK'})


class LoginView(APIView):
    """用户登录"""

    def post(self, request):
        pass
