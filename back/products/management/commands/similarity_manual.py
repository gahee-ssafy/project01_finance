import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import ManualChunk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '질문과 관련된 장을 찾아내고, 본문 내 핵심 수치와 팩트를 전수 조사하여 보고합니다.'

    def add_arguments(self, parser):
        parser.add_argument('user_query', type=str, help='신입사원의 질문')

    def handle(self, *args, **options):
        user_query = options['user_query']
        self.stdout.write(self.style.WARNING(f"🤖 [사수 엔진 가동] DB 열람 및 팩트 추출 중..."))

        # 1. 모델 로드 및 질문 벡터화
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        query_vector = model.encode(user_query).reshape(1, -1)

        # 2. 통합 임베딩 기반 챕터 검색
        targets = ManualChunk.objects.filter(embedding__isnull=False)
        analysis_results = []
        for chunk in targets:
            target_vector = np.frombuffer(chunk.embedding, dtype='float32').reshape(1, -1)
            score = cosine_similarity(query_vector, target_vector)[0][0] * 100
            analysis_results.append({
                'title': chunk.chapter_title,
                'raw_content': chunk.content,
                'score': score
            })

        analysis_results = [res for res in analysis_results if res['score'] >= 35]
        analysis_results.sort(key=lambda x: x['score'], reverse=True)

        if not analysis_results:
            self.stdout.write(self.style.ERROR("\n❌ 관련 규정을 찾을 수 없습니다. 질문을 더 구체적으로 입력하십시오."))
            return

        # 3. [핵심 공정] 1순위 장을 열어서 팩트 문장 추출
        best_match = analysis_results[0]
        query_keywords = [word for word in user_query.split() if len(word) >= 2]
        finance_units = ['%', 'LTV', 'DTI', '한도', '억원', '만원', '금리', '소득']

        # 본문 분해 및 팩트 수집
        sentences = [s.strip() for s in best_match['raw_content'].replace('\n', '.').split('.') if len(s.strip()) > 5]
        
        fact_box = []
        for s in sentences:
            if any(kw in s for kw in query_keywords) or any(unit in s for unit in finance_units):
                if s not in fact_box:
                    fact_box.append(s)

        # 4. 결론 도출 (80% 또는 한도 관련 문장 우선 타격)
        conclusion = ""
        for s in fact_box:
            # 수치 정보가 구체적으로 박힌 문장을 결론으로 채택
            if '80' in s and '%' in s or 'LTV' in s or '한도' in s:
                conclusion = s
                break

        # 5. 최종 사수 스타일 보고서 출력
        self.stdout.write("\n" + "="*85)
        
        if conclusion:
            # 결론이 있을 경우 직설적으로 답변
            self.stdout.write(self.style.SUCCESS(f"🤖 [사수 직답]: 결론부터 말씀드리면, {conclusion} 입니다."))
        else:
            self.stdout.write(self.style.SUCCESS(f"🤖 [사수 직답]: 해당 장에서 질문과 관련된 구체적 수치를 확인하십시오."))

        self.stdout.write("-" * 85)
        self.stdout.write(f"📍 상세 규정은 DB 내 [{best_match['title']}]을 직접 열람하십시오.")
        self.stdout.write(f"   (매칭 정확도: {best_match['score']:.2f}%)")
        self.stdout.write("="*85 + "\n")