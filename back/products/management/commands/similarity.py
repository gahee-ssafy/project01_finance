import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

# SSL 인증서 경로 설정
os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '은행 필터링 후 최저 금리 순으로 상품을 정밀 추천합니다.'

    def add_arguments(self, parser):
        parser.add_argument('user_query', type=str, help='유사도 분석을 위한 사용자 질문')

    def handle(self, *args, **options):
        user_query = options['user_query']
        
        # 1. 엔티티 추출 및 1차 DB 필터링 (필터링 공정)
        # 질문에 포함된 은행명을 찾아서 해당 은행 데이터만 추출
        all_banks = MortgageBaseInfo.objects.values_list('kor_co_nm', flat=True).distinct()
        target_bank = next((bank for bank in all_banks if bank in user_query), None)

        if target_bank:
            self.stdout.write(f"🎯 [{target_bank}] 데이터 필터링 가동...")
            targets = MortgageBaseInfo.objects.filter(kor_co_nm=target_bank, combined_embedding__isnull=False)
        else:
            targets = MortgageBaseInfo.objects.filter(combined_embedding__isnull=False)

        if not targets.exists():
            self.stdout.write(self.style.ERROR("분석 대상 데이터가 없습니다."))
            return

        # 2. 임베딩 모델 로드 및 질문 벡터화
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        query_vector = model.encode(user_query)

        # 3. 코사인 유사도 계산 및 데이터 결합
        analysis_results = []
        for product in targets:
            target_vector = np.array(product.combined_embedding)
            dot_product = np.dot(query_vector, target_vector)
            norm_q = np.linalg.norm(query_vector)
            norm_t = np.linalg.norm(target_vector)
            similarity = dot_product / (norm_q * norm_t) if (norm_q * norm_t) > 0 else 0
            
            analysis_results.append({
                'bank': product.kor_co_nm,
                'name': product.fin_prdt_nm,
                'rate': float(product.lend_rate_min) if product.lend_rate_min else 99.0,
                'score': float(similarity) * 100
            })

        # 4. [핵심 로직] 수치 기반 확정 정렬
        # "낮은", "최저", "금리" 등의 키워드가 있으면 유사도 컷오프(40% 이상) 통과 후 금리순 정렬
        rate_keywords = ['낮은', '최저', '금리', '싼', '저금리']
        is_rate_query = any(word in user_query for word in rate_keywords)

        if is_rate_query:
            # 유사도가 최소한의 맥락(40%)은 맞으면서 금리가 가장 낮은 순으로 정렬
            analysis_results = [res for res in analysis_results if res['score'] >= 40]
            analysis_results.sort(key=lambda x: x['rate']) # 금리 오름차순
        else:
            # 일반적인 맥락 질문은 유사도 순 정렬
            analysis_results.sort(key=lambda x: x['score'], reverse=True)

        # 5. 결과 출력 (상위 5개)
        self.stdout.write(f"\n🔍 분석 결과 보고서 (질문: {user_query})")
        self.stdout.write("-" * 75)
        self.stdout.write(f"{'순위':<4} | {'유사도':<8} | {'금리':<6} | {'은행 및 상품명'}")
        self.stdout.write("-" * 75)
        
        for i, res in enumerate(analysis_results[:5], 1):
            self.stdout.write(f"{i:<4} | {res['score']:>6.2f}% | {res['rate']:>5.2f}% | [{res['bank']}] {res['name']}")
        self.stdout.write("-" * 75)