import os
import ssl

# 1. SSL 및 환경 변수 청소 (최상단 유지)
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]
ssl._create_default_https_context = ssl._create_unverified_context


import numpy as np
from google import genai
from django.core.management.base import BaseCommand
from products.models import ManualChunk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 2. Gemini API 설정 (여기에 본인의 API 키를 넣으세요)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Command(BaseCommand):
    help = '로컬 DB 검색과 Gemini API를 결합한 퍼플렉시티형 시스템입니다.'

    def handle(self, *args, **options):
        # 모델 사전 로드
        self.stdout.write(self.style.NOTICE("⚙️  임베딩 모델 로딩 중..."))
        embed_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        # Gemini 모델 준비 
        llm = genai.GenerativeModel('gemini-3-flash-preview')
        
        self.stdout.write(self.style.SUCCESS("✅ 퍼플렉시티 엔진 준비 완료. 질문을 입력하세요."))

        while True:
            user_query = input("\n💬 질문: ").strip()
            if user_query.lower() in ['exit', 'quit', '종료', 'q']: break
            if not user_query: continue

            self.stdout.write(self.style.WARNING(f"🔍 로컬 DB에서 최적의 근거를 찾는 중..."))

            # ... (상단 SSL 및 Gemini 설정부 동일)

            # 3. 질문 벡터화 및 코사인 유사도 계산
            query_vector = embed_model.encode(user_query).reshape(1, -1)
            targets = ManualChunk.objects.filter(embedding__isnull=False)
            
            analysis_results = []
            for chunk in targets:
                target_vector = np.frombuffer(chunk.embedding, dtype='float32').reshape(1, -1)
                # [수학적 근거] 1.0에 가까울수록 질문과 일치함
                score = float(cosine_similarity(query_vector, target_vector)[0][0])
                analysis_results.append({
                    'title': chunk.chapter_title,
                    'content': chunk.content,
                    'score': score
                })

            # 유사도 기준 내림차순 정렬 후 상위 3개 추출
            analysis_results.sort(key=lambda x: x['score'], reverse=True)
            top_matches = [res for res in analysis_results[:3] if res['score'] >= 0.35]

            if not top_matches:
                self.stdout.write(self.style.ERROR("❌ 검색 결과가 없습니다. (유사도 0.35 미만)"))
                continue

            # 4. Gemini 지능형 답변 생성 (Top-3 컨텍스트 통합)
            combined_context = "\n\n".join([f"[{m['title']}]: {m['content']}" for m in top_matches])
            
            try:
                self.stdout.write(self.style.NOTICE("🧠 Gemini가 검색된 조항들을 통합 분석 중입니다..."))
                prompt = f"질문: {user_query}\n\n[매뉴얼 본문]:\n{combined_context}\n\n위 본문을 근거로 50자 내로 답해."
                response = llm.generate_content(prompt)
                ai_answer = response.text
            except Exception as e:
                ai_answer = f"API 오류 발생: {str(e)}"

            # 5. 최종 보고서 출력 (코사인 유사도 상세 프린트)
            self.stdout.write("\n" + "═"*75)
            self.stdout.write(self.style.SUCCESS(f"🤖 [사수 직답]:\n{ai_answer.strip()}"))
            self.stdout.write("─"*75)
            self.stdout.write(f"📊 [검색 신뢰도 보고서]")
            
            # 검색된 상위 결과들의 유사도를 하나씩 출력합니다.
            for i, match in enumerate(top_matches, 1):
                # 점수에 따라 색상을 다르게 표시하면 더 직관적입니다.
                color_style = self.style.SUCCESS if match['score'] >= 0.6 else self.style.WARNING
                self.stdout.write(color_style(f"   {i}순위: {match['title']} (유사도: {match['score']:.4f})"))
            
            self.stdout.write("═"*75 + "\n")