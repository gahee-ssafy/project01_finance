import os
import certifi
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from sentence_transformers import SentenceTransformer

os.environ['SSL_CERT_FILE'] = certifi.where()

class Command(BaseCommand):
    help = '데이터 통합 필드(combined_content) 생성 및 단일 레코드 검증'

    def handle(self, *args, **options):
        # 1. 엔진 로드
        model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        # 2. 첫 번째 레코드 추출
        product = MortgageBaseInfo.objects.first()
        
        if not product:
            self.stdout.write(self.style.ERROR("처리할 데이터가 DB에 없습니다."))
            return

        # 3. 텍스트 통합 (원문 보존 및 조사 활용)
        combined_text = (
            f"금융회사명은 {product.kor_co_nm}이고, 상품명은 {product.fin_prdt_nm}입니다. "
            f"중도상환수수료 관련 정보는: {product.erly_rpay_fee}"
            f"대출 한도는: {product.loan_lmt}"
            f"금리유형은 {product.lend_rate_type_nm}로, 최저 금리는 {product.lend_rate_min}%입니다. "
        )

        # 4. 시운전 결과 보고 (조회 및 출력)
        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"📝 생성된 통합 텍스트:\n{combined_text}")
        self.stdout.write("="*50 + "\n")

        # 5. 사용자 확인 후 저장 로직 (필드 갱신 없이 신규 필드에 기록)
        product.combined_content = combined_text
        product.embedding = model.encode(combined_text).tolist()
        # product.save()

        self.stdout.write(self.style.SUCCESS(f"✅ ID {product.id}번 레코드의 combined_content 저장 및 임베딩 완료."))
        self.stdout.write("기계적 제언: 출력된 텍스트가 분석 의도에 맞다면, 루프를 돌려 전체 데이터를 처리하십시오.")
