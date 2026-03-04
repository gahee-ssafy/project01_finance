# back/products/views.py

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

from django.db.models import Q, Max

from .models import DepositProducts, SpotPrice
from .serializers import DepositProductsSerializer, SpotPriceSerializer

import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Max


# -----------------------------
# 공통 유틸
# -----------------------------
def _parse_codes(raw: str):
    return [c.strip() for c in (raw or "").split(",") if c.strip()]


# -----------------------------
# [F03] 예적금 상품 목록 조회 (필터/정렬/검색 지원)
# -----------------------------
@api_view(['GET'])
def deposit_products(request):
    """
    GET /api/v1/products/deposit/?bank=우리&term=12&sort=intr_rate2_desc&q=WON

    - bank: 은행명 부분일치 (kor_co_nm)
    - term: 기간(개월) (options__save_trm)
    - q   : 검색어(은행명/상품명)
    - sort:
        - intr_rate2_desc : 최고우대금리(옵션들 중 max intr_rate2) 내림차순
        - intr_rate_desc  : 기본금리(옵션들 중 max intr_rate) 내림차순
        - name_asc        : 상품명 오름차순
        - bank_asc        : 은행명 오름차순
    """
    qs = DepositProducts.objects.all().prefetch_related('options')

    bank = request.GET.get('bank', '').strip()
    term = request.GET.get('term', '').strip()
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '').strip()

    # 은행 필터
    if bank:
        qs = qs.filter(kor_co_nm__icontains=bank)

    # 검색(은행명/상품명)
    if q:
        qs = qs.filter(Q(kor_co_nm__icontains=q) | Q(fin_prdt_nm__icontains=q))

    # 기간 필터 (options.save_trm)
    if term:
        try:
            term_int = int(term)
            qs = qs.filter(options__save_trm=term_int)
        except ValueError:
            pass

    # 정렬용 annotate
    if sort in ('intr_rate2_desc', 'intr_rate_desc'):
        qs = qs.annotate(
            max_intr_rate=Max('options__intr_rate'),
            max_intr_rate2=Max('options__intr_rate2'),
        )

    # 정렬
    if sort == 'intr_rate2_desc':
        qs = qs.order_by('-max_intr_rate2', '-max_intr_rate', 'kor_co_nm', 'fin_prdt_nm')
    elif sort == 'intr_rate_desc':
        qs = qs.order_by('-max_intr_rate', '-max_intr_rate2', 'kor_co_nm', 'fin_prdt_nm')
    elif sort == 'name_asc':
        qs = qs.order_by('fin_prdt_nm')
    elif sort == 'bank_asc':
        qs = qs.order_by('kor_co_nm', 'fin_prdt_nm')
    else:
        qs = qs.order_by('kor_co_nm', 'fin_prdt_nm')

    # options 조인으로 중복될 수 있어서 distinct
    qs = qs.distinct()

    serializer = DepositProductsSerializer(qs, many=True)
    return Response(serializer.data)


# -----------------------------
# [F03-3 연계] 예적금 저장(가입/찜) 토글 API
# -----------------------------
@api_view(["POST", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deposit_join(request, fin_prdt_cd):
    """
    POST   /api/v1/products/deposit/<fin_prdt_cd>/join/   -> 저장(가입/찜)
    DELETE /api/v1/products/deposit/<fin_prdt_cd>/join/   -> 저장 해제
    """
    # 상품 존재 확인
    if not DepositProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
        return Response({"detail": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    user = request.user
    codes = _parse_codes(getattr(user, "financial_products", ""))

    if request.method == "POST":
        if fin_prdt_cd not in codes:
            codes.append(fin_prdt_cd)
    else:  # DELETE
        codes = [c for c in codes if c != fin_prdt_cd]

    user.financial_products = ",".join(codes)
    user.save(update_fields=["financial_products"])

    return Response(
        {"financial_products": user.financial_products, "joined_codes": codes},
        status=status.HTTP_200_OK
    )

# 상세 페이지 조회
from django.shortcuts import get_object_or_404

@api_view(["GET"])
def deposit_detail(request, fin_prdt_cd):
    """
    GET /api/v1/products/deposit/<fin_prdt_cd>/
    - 상품 1개 + options(기간별 금리) 반환
    """
    product = get_object_or_404(
        DepositProducts.objects.prefetch_related("options"),
        fin_prdt_cd=fin_prdt_cd
    )
    serializer = DepositProductsSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)




# -----------------------------
# [F04] 금/은 시세 데이터 조회
# -----------------------------
@api_view(['GET'])
def spot_price(request):
    item_name = request.GET.get('item')  # Gold 또는 Silver

    if item_name:
        prices = SpotPrice.objects.filter(item_name=item_name).order_by('base_date')
    else:
        prices = SpotPrice.objects.all().order_by('base_date')

    serializer = SpotPriceSerializer(prices, many=True)
    return Response(serializer.data)



# [F09] 추천 기능 

def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


@api_view(['POST'])
def recommend(request):
    # 1. 프론트엔드에서 보낸 사용자 입력 받기
    user_input = request.data.get('message')
    
    # 2. 사용자 입력 임베딩 (GMS API)
    GMS_API_KEY=""
    
    url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
    headers = {"Authorization": f"Bearer {GMS_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "text-embedding-3-large", "input": user_input}
    response = requests.post(url, headers=headers, json=payload)
    user_vector = response.json()['data'][0]['embedding']

    # 3. DB 상품들과 유사도 비교
    products = DepositProducts.objects.all().prefetch_related('options') 
    results = []
    
    for p in products:
        score = cosine_similarity(user_vector, p.embedding_vector)
        
        try:
            max_rate = p.options.aggregate(Max('intr_rate2'))['intr_rate2__max']
        except AttributeError:
            max_rate = 0

        results.append({
            'name': p.fin_prdt_nm,
            'bank': p.kor_co_nm,
            'similarity': round(float(score), 4),
            'max_rate': max_rate if max_rate else 0
        })

    # 4. 정렬 후 TOP 3 반환
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return JsonResponse({'recommendations': results[:3]})

