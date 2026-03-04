import requests
import json
from django.core.management.base import BaseCommand
from products.models import DepositProducts
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1. 환경 설정 (Bash의 -H 부분)
        url = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
        gms_key = ""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {gms_key}"
        }

        # 2. DB에서 데이터 가져오기
        products = DepositProducts.objects.all()
        
        self.stdout.write(f"총 {len(products)}개의 상품 임베딩을 시작합니다...")

        for product in products:
            # 3. API 전송 데이터 준비 (Bash의 -d 부분)
            # 교육 자료 4권: 텍스트(Input)를 피쳐로 활용
            payload = {
                "model": "text-embedding-3-large",
                "input": product.spcl_cnd
            }

            # 4. API 호출 (실제 curl 실행과 동일)
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                # 결과에서 숫자 리스트(Embedding)만 쏙 추출
                embedding = response.json()['data'][0]['embedding']
                
                # 5. DB에 영구 저장
                product.embedding_vector = embedding
                product.save()
                self.stdout.write(self.style.SUCCESS(f"상품 [{product.id}] 임베딩 저장 완료!"))
            else:
                self.stdout.write(self.style.ERROR(f"에러 발생: {response.status_code} - {response.text}"))

        self.stdout.write(self.style.SUCCESS("모든 작업이 끝났습니다! 고생하셨어요!"))