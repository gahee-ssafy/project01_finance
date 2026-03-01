from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser의 기본 필드 
    # username, password, first_name, last_name, email, is_staff 등
    
    # 추가 필드
    is_login = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username