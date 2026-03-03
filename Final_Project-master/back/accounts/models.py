from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

class User(AbstractUser):
    # [중요] AbstractUser의 기본 필드
    # username, password, email, first_name, last_name, is_staff, is_active, date_joined 등 기본으로 제공함. 
    # 그러니까, username 따로 필드를 만들 필요가 없는 것. 
    # 추가 필드
        
    @receiver(user_logged_in)
    def on_user_login(sender, request, user, **kwargs):
        user.is_login = True
        user.save()  # 기계적으로 DB에 기록을 확정합니다.

    @receiver(user_logged_out)
    def on_user_logout(sender, request, user, **kwargs):
        if user:
            user.is_login = False
            user.save()  # 로그아웃 시에도 반드시 기록을 확정합니다.
            
    def __str__(self):
        return self.username
    