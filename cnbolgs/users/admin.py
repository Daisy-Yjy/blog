from django.contrib import admin

from .models import User, GithubUser

admin.site.register(User)
admin.site.register(GithubUser)
