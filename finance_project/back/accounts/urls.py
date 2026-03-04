from django.urls import path, include
from .views import CustomRegisterView

urlpatterns = [
    # [중요] dj_rest_auth 라이브러리 사용 
    # login/, logout/ 외 3건 자동으로 url을 제공하고 기능도 제공함. 
    path('', include('dj_rest_auth.urls')),
    
    # 회원가입
    # 클래스로 작성한 CustomRegisterView를 사용하여 회원가입 기능을 제공하는 URL 패턴을 추가합니다.
    # [중요] 클래스에 사용한 RegisterSerializer는 기본적으로 username, password, email을 이미 처리합니다.
    path('signup/', CustomRegisterView.as_view(), name='signup')

]
