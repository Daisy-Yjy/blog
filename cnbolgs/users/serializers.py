import re
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from .models import User, GithubUser
from cnbolgs import settings


class RegisterViewSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""

    password2 = serializers.CharField(label='确认密码', write_only=True)
    email_code = serializers.CharField(label='邮箱验证码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'password', 'password2', 'sms_code', 'allow', 'token', 'email_code', 'email']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20字符的用户名',
                    'max_length': '仅允许5-20字符的用户名'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20字符的密码',
                    'max_length': '仅允许8-20字符的密码'
                }
            },
        }

    def validate_mobile(self, value):
        """单独校验手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """单独校验是否通过协议"""
        if value != '1':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        """"校验密码、验证码"""
        if attrs['password2'] != attrs['password']:
            raise serializers.ValidationError('两个密码不一致')
        redis_conn_sms = get_redis_connection('sms_codes')
        real_sms_code = redis_conn_sms.get('sms_%s' % attrs['mobile'])
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        redis_conn_email = get_redis_connection('email_codes')
        real_email_code = redis_conn_email.get('email_%s' % attrs['email'])
        if real_email_code is None or attrs['email_code'] != real_email_code.decode():
            raise serializers.ValidationError('邮箱验证码错误')
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['allow']
        del validated_data['sms_code']
        del validated_data['email_code']

        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt_payload_handler函数(生成payload)
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 生成jwt
        payload = jwt_payload_handler(user)  # 根据user生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成完整的jwt
        user.token = token

        return user


class LoginViewSerializer(serializers.ModelSerializer):
    """用户登录序列化器"""
    sms_code = serializers.CharField(label='验证码', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'mobile', 'password', 'sms_code', 'token']


class GithubUserViewSerializer(serializers.Serializer):
    """openid绑定序列化器"""

    openid_token = serializers.CharField(label='openid')
    mobile = serializers.CharField(label='手机号')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate_mobile(self, value):
        """单独校验手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate(self, attrs):
        # 解密openid
        openid_token = attrs.pop('openid_token')
        serializer = TJWSSerializer(settings.SECRET_KEY, 600)
        try:
            data = serializer.loads(openid_token)
            openid = data.get('openid')
        except BadData:
            openid = None
        if openid is None:
            raise serializers.ValidationError('openid无效')
        # openid 加入到字典中
        attrs['openid'] = openid

        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('sms_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None or real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:  # 如果没有用户创建一个新用户
            mobile = validated_data.get('mobile')
            password = validated_data.get('password')
            user = User.objects.create(username=mobile, mobile=mobile)
            user.set_password(password)
            user.save()
        # openid与用户绑定
        openid = validated_data.get('openid')
        GithubUser.objects.create(openid=openid, user=user)
        return user






