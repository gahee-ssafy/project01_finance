import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '미생성된 임베딩만 골라서 생성하고 유사도를 분석합니다.'

    def add_arguments(self, parser):
        parser.add_argument('user_query', type=str, nargs='?', default=None, help='분석할 질문')

    def handle(self, *args, **options):
        # 1. 엔진 가동
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Null 데이터만 타겟팅 (최적화 핵심)
        # embedding 필드가 null이거나 비어있는 데이터만 가져옵니다.
        targets = MortgageBaseInfo.objects.filter(
            search_content__isnull=False,
            embedding__isnull=True
        ).exclude(search_content='')
        
        count = targets.count()
        
        if count > 0:
            self.stdout.write(f"📦 새롭게 발견된 {count}개의 데이터를 가공합니다...")
            for i, product in enumerate(targets, 1):
                product.embedding = model.encode(product.search_content).tolist()
                product.save()
                if i % 10 == 0 or i == count:
                    self.stdout.write(f"   작업 중: {i}/{count}")
            self.stdout.write(self.style.SUCCESS("✅ 신규 데이터 임베딩 완료."))
        else:
            self.stdout.write("ℹ️ 모든 데이터가 이미 임베딩되어 있습니다. 추가 작업을 생략합니다.")

        
        # ... (상단 생략: 모델 로드 및 임베딩 생성 로직은 동일)

        # 3. 가변 입력값 분석 (검증)
        user_query = options['user_query']
        if user_query:
            self.stdout.write(f"\n🔍 분석 요청: '{user_query}'")
            query_vector = model.encode(user_query)
            
            all_data = MortgageBaseInfo.objects.filter(embedding__isnull=False)
            results = []
            for product in all_data:
                target_vector = np.array(product.embedding)
                
                # 코사인 유사도 연산
                similarity = np.dot(query_vector, target_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(target_vector))
                
                # 상품명(fin_prdt_nm)과 금융회사명(kor_co_nm)을 조합하여 더 명확하게 표시
                results.append({
                    'name': f"{product.kor_co_nm} - {product.fin_prdt_nm}", 
                    'score': float(similarity) * 100  # 백분율 변환
                })

            # 점수순 정렬
            results.sort(key=lambda x: x['score'], reverse=True)
            
            self.stdout.write("\n--- [유사도 순위 보고서] ---")
            for res in results[:3]:
                # 유사도: 00% 형식으로 출력
                self.stdout.write(f"유사도: {res['score']:.1f}% | 상품명: {res['name']}")
                