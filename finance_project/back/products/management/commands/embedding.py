import os
import certifi
import json
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

# 모델 받으러 허깅페이스 접속하면서 ssl 찾음  
os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '무료 로컬 모델을 사용하여 search_content의 임베딩을 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write("임베딩 모델 로드 중 ...")
        model = SentenceTransformer('all-MiniLM-L6-v2') 
        
        # 2. 전처리된 데이터 타겟팅
        # TODO: 이후 다른 테이블 생성시 targets 변경 
        targets = MortgageBaseInfo.objects.filter(search_content__isnull=False).exclude(search_content='')
        total = targets.count()
        self.stdout.write(f"총 {total}개의 데이터를 임베딩합니다.")

        # 3. 데이터 루프 (수정된 부분: i와 product를 분리)
        for i, product in enumerate(targets, 1):
            # 임베딩 생성
            embedding = model.encode(product.search_content)
            
            # DB 객체 필드에 값 할당 및 저장
            # (주의: models.py에 embedding 필드가 생성되어 있어야 함)
            product.embedding = embedding.tolist()
            product.save()

            # 진행 상황 출력
            if i % 10 == 0 or i == total:
                self.stdout.write(f"진행 상황: {i}/{total}")

        self.stdout.write(self.style.SUCCESS("무료 모델 기반 임베딩 생성 완료."))
