import random
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_response_payload_handler
from rest_framework_jwt.views import ObtainJSONWebToken
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
import requests

from .models import User, GithubUser
from .serializers import RegisterViewSerializer, GithubUserViewSerializer, ForgetPasswordSerializer
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


def github_token(code):
    """
    通过传入的 code 参数，带上client_id、client_secret、和code请求GitHub，以获取access_token
    :param code: 重定向获取到的code参数
    :return: 成功返回access_token；失败返回None；
    """
    token_url = 'https://github.com/login/oauth/access_token?' \
                'client_id={}&client_secret={}&code={}'
    token_url = token_url.format(settings.GITHUB_APP_ID, settings.GITHUB_KEY, code)
    header = {
        'accept': 'application/json'
    }
    res = requests.post(token_url, headers=header)
    if res.status_code == 200:
        res_dict = res.json()
        return res_dict['access_token']
    return None


def github_user(access_token):
    """
    通过传入的access_token，带上access_token参数，向GitHub用户API发送请求以获取用户信息；
    :param access_token: 用于访问API的token
    :return: 成功返回用户信息，失败返回None
    """
    user_url = 'https://api.github.com/user'
    access_token = 'token {}'.format(access_token)
    headers = {
        'accept': 'application/json',
        'Authorization': access_token
    }
    res = requests.get(user_url, headers=headers)
    if res.status_code == 200:
        user_info = res.json()
        print(22, user_info)
        return user_info
    return None


class GithubUserView(APIView):
    """github第三方登录处理"""

    def get(self, request):

        req_code = request.query_params.get('code', None)  # 获取授权码code
        if not req_code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            access_token = github_token(req_code)  # 向GitHub发送请求以获取access_token
            user_info = github_user(access_token)  # 向GitHub用户API发送请求获取信息
            if user_info:
                openid = user_info.get('id')
        except:
            return Response({'message': 'Github服务器不可用'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 查询数据库有没有该openid
        try:
            auth_github_user = GithubUser.objects.get(openid=openid)
        except GithubUser.DoesNotExist:
            # 没有绑定openid，加密返回openid给前端暂存 备用
            serializer = TJWSSerializer(settings.SECRET_KEY, 600)
            data = {'openid': openid}
            token = serializer.dumps(data)  # 字节类型
            openid_token = token.decode()
            return Response({'openid_token': openid_token})
        else:
            user = auth_github_user.user
            # 生成token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt_payload_handler函数(生成payload)
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt
            payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
            token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
            return Response({'token': token, 'username': user.username, 'user_id': user.id})

    def post(self, request):
        """openid调用接口绑定"""

        serializer = GithubUserViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        return Response({'token': token, 'username': user.username, 'user_id': user.id})


class ForgetUsernamePassword(APIView):
    """忘记用户名和密码"""

    def get(self, request, email):
        """忘记用户名"""

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': '该邮箱未注册'})
        else:
            username = user.username
            subject = "cnblog登录用户名找回"  # 邮件主题/标题
            html_message = '<p>您好，您在cnblog的登录名是：%s' % username
            # send_mail(subject:标题, message:普通邮件正文, 发件人, [收件人], html_message=超文本的邮件内容)
            send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
            return Response({'message': 'OK'})

    def post(self, request):
        """忘记密码"""

        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        return Response({'token': token, 'username': user.username, 'user_id': user.id})
