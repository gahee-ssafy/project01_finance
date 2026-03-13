import json
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

class Command(BaseCommand):
    help = '무료 로컬 모델을 사용하여 search_content의 임베딩을 생성합니다.'

    def handle(self, *args, **options):
        # 1. 모델 로드 (최초 실행 시 자동 다운로드)
        self.stdout.write("임베딩 모델 로드 중 ...")
        model = SentenceTransformer('all-MiniLM-L6-v2')  # 무료 모델 중 하나 선택

        # 2. 전처리된 데이터 타겟팅
        # TODO: 이후 다른 테이블 생성시 필드 변경 
        targets = MortgageBaseInfo.objects.filter(search_content__isnull=False).exclude(search_content='')
        total = targets.count()
        self.stdout.write(f"총 {total}개의 데이터를 임베딩합니다.")

        for i, product in enumerate(targets, 1):
            # 3. 임베딩 생성 (텍스트 -> 768차원 숫자 리스트)
            embedding = model.encode(product.search_content)
            
            # 4. DB 저장 (리스트 형태로 변환하여 저장)
            product.embedding = embedding.tolist()
            product.save()

            if i % 10 == 0:
                self.stdout.write(f"진행 상황: {i}/{total}")

        self.stdout.write(self.style.SUCCESS("무료 모델 기반 임베딩 생성 완료."))