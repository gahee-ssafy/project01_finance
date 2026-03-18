import os
import certifi
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    def handle(self, *args, **options):
        help = "combined_content를 생성하고 임베딩을 수행합니다."
        # 1. 엔진 로드
        self.stdout.write("🚀 ko-sroberta 엔진 가동 중...")
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        # 2. 전체 데이터 호출
        targets = MortgageBaseInfo.objects.all()
        total = targets.count()
        
        self.stdout.write(f"📊 수치 결합 공정 시작: 총 {total}건")

        for i, product in enumerate(targets, 1):
            # [수정된 통합 로직] 수치와 조건 필드를 문맥으로 결합
            combined_text = (
                f"금융회사명은 {product.kor_co_nm}이고, 상품명은 {product.fin_prdt_nm}입니다. "
                f"중도상환수수료 관련 정보는: {product.erly_rpay_fee_float}% "
                f"대출 한도는: {product.loan_lmt} "
                f"금리유형은 {product.lend_rate_type_nm}로, 최저 금리는 {product.lend_rate_min}%입니다."
            )

            # 필드 갱신 및 저장
            product.combined_content = combined_text
            # [임베딩] 수치 정보가 포함된 문장을 벡터로 변환
            product.combined_embedding = model.encode(combined_text).tolist()
            product.save()

            if i % 10 == 0 or i == total:
                self.stdout.write(f"🔄 처리 중: {i}/{total} ({(i/total)*100:.1f}%)")

        self.stdout.write(self.style.SUCCESS("\n✨ 수치 정보 기반 통합 임베딩이 모두 완료되었습니다."))
