import requests
import numpy as np
from django.core.management.base import BaseCommand
from products.models import DepositProducts
from django.conf import settings

# [교육자료 4권] 코사인 유사도: 두 벡터의 '방향'이 얼마나 일치하는지 계산
def cosine_similarity_manual(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. 사용자 입력 (이게 우리의 '새로운 피쳐'입니다!)
        user_input = "20대 사회초년생인데, 첫 월급으로 시작하기 좋은 고금리 적금 추천해줘"
        self.stdout.write(f"사용자 입력: '{user_input}'\n")

        # 2. GMS API 호출 (사용자 입력을 숫자로 변환하는 과정 - 필수!)
        url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
        gms_key = ""
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {gms_key}"}
        payload = {"model": "text-embedding-3-large", "input": user_input}

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # 드디어 'user_vector'가 탄생했습니다!
            user_vector = response.json()['data'][0]['embedding']
        else:
            self.stdout.write(self.style.ERROR(f"API 에러: {response.text}"))
            return

        # 3. DB에서 상품 정보 가져오기
        products = DepositProducts.objects.exclude(embedding_vector__isnull=True)
        results = []

        for product in products:
            # 이미 저장된 상품 벡터와 지금 만든 사용자 벡터 비교
            sim_score = cosine_similarity_manual(user_vector, product.embedding_vector)
            results.append((product.fin_prdt_nm, sim_score, product.kor_co_nm))

        # 4. 유사도 높은 순으로 정렬
        results.sort(key=lambda x: x[1], reverse=True)

        # 5. 결과 출력
        self.stdout.write(self.style.SUCCESS("--- 추천 결과 TOP 3 ---"))
        for i, (name, score, bank) in enumerate(results[:3]):
            self.stdout.write(f"{i+1}위: [{bank}] {name} (유사도: {score:.4f})")