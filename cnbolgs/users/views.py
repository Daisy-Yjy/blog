import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_response_payload_handler
from rest_framework_jwt.views import ObtainJSONWebToken

from .models import User
from .serializers import RegisterViewSerializer
from libs.yuntongxun import sms
from cnbolgs import settings
from .utils import jwt_response_payload_handler


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


class LoginAccountView(ObtainJSONWebToken):
    """用户昵称和邮箱登录"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginMobileView(APIView):
    """手机号验证码登录"""

    def post(self, request, *args, **kwargs):
        mobile = request.mobile
        sms_code = request.sms_code
        user = request.user
        redis_conn_sms = get_redis_connection('sms_codes')
        real_sms_code = redis_conn_sms.get('sms_%s' % mobile)
        if real_sms_code is None or sms_code != real_sms_code.decode():
            return Response({'message': '短信验证码错误'})

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        user.token = token
        response_data = {'user_id': user.id, 'username': user.username, 'token': token}
        return Response(response_data)
