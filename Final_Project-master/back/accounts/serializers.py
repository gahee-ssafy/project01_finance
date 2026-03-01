from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    # [중요] RegisterSerializer는 기본적으로 username, password, email을 이미 처리합니다.

    def save(self, request):
        # 기본 유저 정보를 생성
        user = super().save(request)
        
        # 가입 시점에는 로그인 상태가 아니므로 False를 강제합니다.
        user.is_login = False
        user.save()
        
        return user