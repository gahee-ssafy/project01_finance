import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

# SSL 인증서 경로 설정
os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '입력값과 DB의 combined_content 임베딩 간 코사인 유사도를 분석합니다.'

    def add_arguments(self, parser):
        # 가변 입력값을 받기 위한 인자 설정
        parser.add_argument('user_query', type=str, help='유사도 분석을 위한 사용자 질문')

    def handle(self, *args, **options):
        # 1. 입력값 수신
        user_query = options['user_query']
        
        # 2. 임베딩 모델 로드 (엔진 가동)
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        # 3. 입력값 -> 임베딩 (벡터 변환)
        query_vector = model.encode(user_query)

        # 4. 코사인 유사도 분석 시작
        # combined_content 필드에 대응하는 embedding 데이터가 있는 레코드만 호출
        targets = MortgageBaseInfo.objects.filter(combined_embedding__isnull=False)
        
        if not targets.exists():
            self.stdout.write(self.style.ERROR("DB에 분석할 임베딩 데이터가 없습니다."))
            return

        analysis_results = []

        for product in targets:
            # DB에 저장된 벡터를 Numpy 배열로 변환
            target_vector = np.array(product.combined_embedding)
            
            # 수학적 코사인 유사도 연산
            dot_product = np.dot(query_vector, target_vector)
            norm_q = np.linalg.norm(query_vector)
            norm_t = np.linalg.norm(target_vector)
            similarity = dot_product / (norm_q * norm_t) if (norm_q * norm_t) > 0 else 0
            
            analysis_results.append({
                'bank': product.kor_co_nm,
                'name': product.fin_prdt_nm,
                'score': float(similarity) * 100
            })

        # 5. 유사도 점수 기준 내림차순 정렬
        analysis_results.sort(key=lambda x: x['score'], reverse=True)

        # 6. 결과 출력 (분석 보고서)
        self.stdout.write(f"\n🔍 분석 결과 보고서 (질문: {user_query})")
        self.stdout.write("-" * 60)
        for res in analysis_results[:5]:
            self.stdout.write(f"유사도: {res['score']:>6.2f}% | [{res['bank']}] {res['name']}")
        self.stdout.write("-" * 60)