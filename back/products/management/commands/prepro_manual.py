import os
import certifi
from django.core.management.base import BaseCommand
from products.models import ManualChunk # 모델명 확인
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '매뉴얼의 제목과 본문을 결합하여 벡터 임베딩을 수행합니다.'

    def handle(self, *args, **options):
        # 1. SBERT 엔진 로드
        self.stdout.write(self.style.SUCCESS("🚀 ko-sroberta 엔진 가동 중..."))
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        # 2. 전체 데이터 호출 (임베딩이 필요한 데이터 위주)
        targets = ManualChunk.objects.all()
        total = targets.count()
        
        self.stdout.write(f"📊 매뉴얼 문맥 결합 공정 시작: 총 {total}건")

        for i, chunk in enumerate(targets, 1):
            # [수정된 문맥 결합 로직]
            # 챕터 제목과 본문을 자연스러운 문장으로 결합하여 검색 엔진이 이해하기 쉽게 만듭니다.
            combined_text = (
                f"이 내용은 {chunk.chapter_title}에 대한 설명입니다. "
                f"주요 지침 내용은 다음과 같습니다: {chunk.content}"
            )

            # 3. 임베딩 및 바이너리 변환 저장
            # 앞서 작성한 검색 로직과 호환되도록 numpy 바이너리(float32) 형태로 저장합니다.
            embedding_vector = model.encode(combined_text)
            
            # Django 모델의 BinaryField에 맞게 변환
            chunk.embedding = embedding_vector.astype('float32').tobytes()
            
            # (선택 사항) combined_content 필드가 있다면 저장
            if hasattr(chunk, 'combined_content'):
                chunk.combined_content = combined_text
            
            chunk.save()

            # 진행률 보고 (기계적 피드백)
            if i % 5 == 0 or i == total:
                self.stdout.write(f"🔄 처리 중: {i}/{total} ({(i/total)*100:.1f}%)")

        self.stdout.write(self.style.SUCCESS("\n✨ 매뉴얼 문맥 기반 통합 임베딩이 모두 완료되었습니다."))