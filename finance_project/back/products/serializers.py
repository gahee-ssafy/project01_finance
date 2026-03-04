from rest_framework import serializers
from .models import DepositProducts, DepositOptions, SpotPrice

# 1. 예적금 상품 Serializer
class DepositOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOptions
        fields = '__all__'
        read_only_fields = ('product',) # 읽기 전용 설정

class DepositProductsSerializer(serializers.ModelSerializer):
    # 역참조를 통해 옵션 정보도 같이 포함 (related_name='options' 필수)
    options = DepositOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProducts
        fields = '__all__'

# 2. 금/은 시세 Serializer
class SpotPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotPrice
        fields = '__all__'