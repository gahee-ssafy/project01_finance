from dj_rest_auth.registration.views import RegisterView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from .serializers import (
    CustomRegisterSerializer,          
)

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
