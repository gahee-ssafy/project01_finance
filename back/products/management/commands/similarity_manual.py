import os
import certifi
import numpy as np
from django.core.management.base import BaseCommand
from products.models import ManualChunk
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '사용자 질문 의도를 파악하여 관련 매뉴얼 챕터를 정밀 검색 및 정렬합니다.'

    def add_arguments(self, parser):
        parser.add_argument('user_query', type=str, help='분석할 신입사원의 질문')

    def handle(self, *args, **options):
        user_query = options['user_query']
        self.stdout.write(self.style.WARNING(f"🤖 [RAG 엔진 가동] 질문: {user_query}"))

    # 1. 모델 로드 및 질문 벡터화
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        query_vector = model.encode(user_query)

        # 2. 검색 대상 필터링 (임베딩이 있는 데이터만)
        targets = ManualChunk.objects.filter(embedding__isnull=False)
        
        analysis_results = []
        for chunk in targets:
            # BinaryField에서 벡터 복구
            target_vector = np.frombuffer(chunk.embedding, dtype='float32')
            
            # 코사인 유사도 연산
            similarity = np.dot(query_vector, target_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(target_vector)
            )
            
            analysis_results.append({
                'title': chunk.chapter_title,
                'content': chunk.content[:100].replace('\n', ' ') + "...", # 요약 표시용
                'score': float(similarity) * 100,
                'raw_content': chunk.content
            })

        # 3. [지능형 필터링 및 우선순위 조정]
        # 유사도 35% 미만은 관련 없는 것으로 간주 (컷오프)
        analysis_results = [res for res in analysis_results if res['score'] >= 35]

        # 특정 키워드 포함 시 가산점 부여 (예: '신혼' 언급 시 관련 챕터 상향)
        priority_keywords = ['신혼', '생애최초', '전세사기', '한도', '중도상환']
        for res in analysis_results:
            if any(word in user_query and word in res['title'] for word in priority_keywords):
                res['score'] += 10  # 키워드 매칭 시 스코어 보정 (부스팅)

        # 유사도 점수 높은 순으로 정렬
        analysis_results.sort(key=lambda x: x['score'], reverse=True)

        # 4. 분석 리포트 출력
        self.stdout.write("\n📚 매뉴얼 검색 결과 보고서")
        self.stdout.write("=" * 85)
        self.stdout.write(f"{'순위':<4} | {'유사도':<8} | {'장 제목'}")
        self.stdout.write("-" * 85)
        
        if not analysis_results:
            self.stdout.write(self.style.ERROR("검색 결과가 없습니다. 질문을 더 구체적으로 입력해 주세요."))
        else:
            for i, res in enumerate(analysis_results[:3], 1): # 상위 3개만 출력
                self.stdout.write(f"{i:<4} | {res['score']:>6.2f}% | {res['title']}")
                self.stdout.write(f"   ㄴ [미리보기]: {res['content']}")
        self.stdout.write("=" * 85)