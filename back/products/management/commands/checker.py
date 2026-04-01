# app/management/commands/checker.py
import torch
import numpy as np
from django.core.management.base import BaseCommand
from models import ManualChunk
from sentence_transformers import SentenceTransformer, util

class Command(BaseCommand):
    help = '매뉴얼 기반 대출 한도 분석 (하드코딩 데이터 적용)'

    def handle(self, *args, **options):
        # --- [하드코딩 입력값 영역] ---
        price = 400000000          # 주택가격: 4억 원
        income_type = 'recognized'  # 소득종류: 인정소득
        deposit = 200000000         # 전세보증금: 2억 원 (가정치)
        # -----------------------------

        self.stdout.write(self.style.WARNING(f"입력 데이터: 가격 {price:,}원, 소득유형 {income_type}, 보증금 {deposit:,}원\n"))

        # 1. SBERT 모델 로드 및 근거 검색 (RAG)
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        search_query = f"{income_type} 소득 산정 시 LTV 담보인정비율 제한 규정"
        query_emb = model.encode(search_query, convert_to_tensor=True)

        # 2. SQLite에서 가장 관련 있는 근거 조항 검색
        chunks = ManualChunk.objects.all()
        best_chunk, max_sim = None, -1.0

        for chunk in chunks:
            stored_emb = torch.from_numpy(np.frombuffer(chunk.embedding, dtype=np.float32))
            sim = util.cos_sim(query_emb, stored_emb).item()
            if sim > max_sim:
                max_sim, best_chunk = sim, chunk

        # 3. 매뉴얼 기반 논리 연산 (제7장 및 제15장 규정 참조)
        # 인정소득 시 LTV 60% 제한 [cite: 7, 15]
        if income_type == 'recognized':
            ltv_ratio = 0.6  
            rule_ref = "제7장 1. 2) (3)" [cite: 7]
        else:
            ltv_ratio = 0.7  
            rule_ref = "제7장 1. 1)" [cite: 7]

        # 4. 최종 한도 계산: (가격 * LTV) - 선순위 채권
        # 보금자리론 일반 한도 3.6억 원 적용 [cite: 4]
        calc_limit = (price * ltv_ratio) - deposit
        final_loan_amount = max(0, min(calc_limit, 360000000)) [cite: 4]

        # 5. 근거 조항 중심 리포트 출력
        self.stdout.write(self.style.SUCCESS(f"🎯 최종 대출 가능액: {final_loan_amount:,.0)원"))
        self.stdout.write(f"💡 판단 근거: {rule_ref} 규정에 따라 LTV {int(ltv_ratio*100)}% 적용")
        self.stdout.write(f"📄 매뉴얼 {best_chunk.page_number}p 근거 원문:")
        self.stdout.write(f"   \"{best_chunk.content[:200]}...\"")
