from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

# 이 클래스는 회원가입 시 추가적으로 처리할 로직이 있다면 여기에 작성하면 됩니다.
class CustomRegisterSerializer(RegisterSerializer):
    # [중요] RegisterSerializer는 기본적으로 username, password, email을 이미 처리합니다.
    def save(self, request):
        # 기본 유저 정보 
        user = super().save(request)
        
        # 가입 시점에는 로그인 상태가 아니므로 False를 강제합니다.
        # 추가 필드이므로 직접 설정해주는 것이 안전합니다.
        user.is_login = False

        # 유저 정보를 저장합니다.
        user.save()
        
        return user