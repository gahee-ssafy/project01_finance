import numpy as np
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

class Command(BaseCommand):
    help = '하드코딩된 입력값을 바탕으로 DB 내 상품들과 코사인 유사도를 분석합니다.'

    def handle(self, *args, **options):
        # 1. 하드코딩된 테스트 입력값 (영점 조절)
        test_input = "금리가 가장 낮은 아파트 담보대출을 찾고 있어"
        self.stdout.write(f"🔍 입력값 분석 중: '{test_input}'")

        # 2. AI 모델 로드
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 3. 입력값 벡터화
        query_vector = model.encode(test_input)

        # 4. DB 데이터 호출 (임베딩이 있는 것만)
        targets = MortgageBaseInfo.objects.filter(embedding__isnull=False)
        
        if not targets.exists():
            self.stdout.write(self.style.ERROR("DB에 임베딩 데이터가 없습니다. 먼저 embedding 명령을 실행하세요."))
            return

        analysis_results = []

        # 5. 유사도 연산 루프
        for product in targets:
            target_vector = np.array(product.embedding)
            
            # 코사인 유사도 계산
            dot_product = np.dot(query_vector, target_vector)
            norm_query = np.linalg.norm(query_vector)
            norm_target = np.linalg.norm(target_vector)
            
            similarity = dot_product / (norm_query * norm_target) if (norm_query * norm_target) > 0 else 0
            
            analysis_results.append({
                'name': product.fin_prdt_nm,
                'score': float(similarity),
            })

        # 6. 결과 정렬 및 출력
        analysis_results.sort(key=lambda x: x['score'], reverse=True)

        self.stdout.write("\n=== 유사도 분석 결과 (Top 3) ===")
        for res in analysis_results[:3]:
            self.stdout.write(f"[{res['score']:.4f}] {res['name']}")