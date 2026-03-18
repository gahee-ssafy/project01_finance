import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '금리 및 중도상환수수료 의도를 파악하여 최적의 상품을 정밀 정렬합니다.'

    def add_arguments(self, parser):
        parser.add_argument('user_query', type=str, help='유사도 분석을 위한 사용자 질문')

    def handle(self, *args, **options):
        user_query = options['user_query']
        
        # 1. 은행 필터링
        all_banks = MortgageBaseInfo.objects.values_list('kor_co_nm', flat=True).distinct()
        target_bank = next((bank for bank in all_banks if bank in user_query), None)

        targets = MortgageBaseInfo.objects.filter(kor_co_nm=target_bank) if target_bank else MortgageBaseInfo.objects.all()
        targets = targets.filter(combined_embedding__isnull=False)

        # 2. 임베딩 및 코사인 유사도 연산
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        query_vector = model.encode(user_query)

        analysis_results = []
        for product in targets:
            target_vector = np.array(product.combined_embedding)
            similarity = np.dot(query_vector, target_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(target_vector))
            
            analysis_results.append({
                'bank': product.kor_co_nm,
                'name': product.fin_prdt_nm,
                # NULL(None) 데이터 처리: 금리는 99%, 수수료는 9.9%로 밀어버림 (오름차순 대비)
                'rate': float(product.lend_rate_min) if product.lend_rate_min else 99.0,
                'fee': float(product.erly_rpay_fee_float) if product.erly_rpay_fee_float is not None else 9.9,
                'score': float(similarity) * 100
            })

        # 3. [지능형 정렬 로직]
        # 키워드 포착
        fee_keywords = ['중도상환', '수수료', '일찍', '중도']
        is_fee_query = any(word in user_query for word in fee_keywords)
        
        # 유사도 40% 미만은 문맥 외 질문으로 간주하고 필터링
        analysis_results = [res for res in analysis_results if res['score'] >= 40]

        if is_fee_query:
            # 중도상환 질문 시: 수수료 낮은 순 -> 금리 낮은 순 (복합 정렬)
            self.stdout.write("⚙️ [수수료 중심] 정렬 알고리즘 가동...")
            analysis_results.sort(key=lambda x: (x['fee'], x['rate']))
        else:
            # 일반/금리 질문 시: 금리 낮은 순 (기본 제안)
            self.stdout.write("⚙️ [금리 중심] 기본 정렬 알고리즘 가동...")
            analysis_results.sort(key=lambda x: x['rate'])

        # 4. 분석 리포트 출력
        self.stdout.write(f"\n🔍 분석 결과 보고서 (질문: {user_query})")
        self.stdout.write("-" * 85)
        self.stdout.write(f"{'순위':<4} | {'유사도':<8} | {'금리':<6} | {'수수료':<6} | {'은행 및 상품명'}")
        self.stdout.write("-" * 85)
        
        for i, res in enumerate(analysis_results[:5], 1):
            fee_display = f"{res['fee']:.2f}%" if res['fee'] != 9.9 else "NULL"
            self.stdout.write(f"{i:<4} | {res['score']:>6.2f}% | {res['rate']:>5.2f}% | {fee_display:>6} | [{res['bank']}] {res['name']}")
        self.stdout.write("-" * 85)