from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    # 判断用户名是否已注册
    re_path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    # 判断手机号是否已注册
    re_path(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/', views.MobileCountView.as_view()),
    # 判断邮箱是否已注册
    re_path(r'email/(?P<email>[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3})/count/', views.EmailCountView.as_view()),
    # 发送邮箱验证码
    re_path(r'email_codes/(?P<email>[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3})/', views.VerifyEmail.as_view()),
    # 发送短信验证码
    re_path(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    # 用户注册
    path('register/', views.RegisterView.as_view()),
    # 用户账号登录
    path('login/account/', views.LoginAccountView.as_view()),
    # path('login/account/', views.LoginView.as_view({'post': 'account'})),
    # 用户手机号登录
    path('login/mobile/', views.LoginMobileView.as_view()),
    # path('login/mobile/', views.LoginView.as_view({'post': 'mobile'})),
    # path(r'^login/$', obtain_jwt_token),
]
