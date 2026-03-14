import re
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from kiwipiepy import Kiwi

class Command(BaseCommand):
    help = '금융 조건(LTV, 수수료, 금리) 영점을 재조정하여 전처리를 수행합니다.'

    kiwi = Kiwi()
    STOPWORDS = {'인지세', '채권', '매입', '근저당권', '설정', '비용', '확인', '제공', '부담', '대상', '관련'}

    def extract_priority_values(self, product):
        """[재조정] 금리체계, LTV(loan_lmt 필드), 중도상환수수료(소수점 대응) 추출"""
        
        # 1. 금리체계
        rate_type = product.lend_rate_type_nm or "금리유형미비"
        
        # 2. LTV 추출 (사용자 지침에 따라 loan_lmt 필드 참조)
        ltv_text = product.loan_lmt or ""
        # '70%', '70%이내', 'LTV 70' 등 다양한 패턴 대응
        ltv_match = re.search(r'(\d{1,3}%?)', ltv_text)
        ltv_val = f"LTV{ltv_match.group(1)}" if ltv_match else "LTV정보미비"
        
        # 3. 중도상환수수료 추출 (소수점 패턴 대응: 0.71%, 0.95% 등)
        fee_text = product.erly_rpay_fee or ""
        # 숫자 + 점(.) + 숫자 + % 패턴을 모두 찾아 리스트화
        fee_matches = re.findall(r'\d+\.?\d*%', fee_text)
        
        # 중복 제거 후 "수수료0.71%/0.95%" 형태로 결합
        if fee_matches:
            unique_fees = list(dict.fromkeys(fee_matches))
            fee_val = f"수수료{'/'.join(unique_fees)}"
        else:
            fee_val = "수수료0%"
        
        return f"[{rate_type} {ltv_val} {fee_val}]"

    def clean_context(self, text, limit=10):
        """나머지 핵심 키워드 10개 추출"""
        if not text: return ""
        res = self.kiwi.analyze(text)
        tokens = []
        for result, score in res:
            for token in result:
                if token.tag in ['NNG', 'NNP', 'SL']:
                    if token.form not in self.STOPWORDS and len(token.form) > 1:
                        if token.form not in tokens:
                            tokens.append(token.form)
        return " ".join(tokens[:limit])

    def handle(self, *args, **options):
        targets = MortgageBaseInfo.objects.all()
        self.stdout.write(f"영점 재조정 루틴 가동: {targets.count()}개 대상")

        for product in targets:
            # 1순위: 금융 조건 (영점 타격 완료)
            priority_chunk = self.extract_priority_values(product)
            
            # 2순위: 브랜드 및 상품명
            secondary_context = self.clean_context(f"{product.kor_co_nm} {product.fin_prdt_nm}")
            
            # 3순위: 데이터 결합
            product.search_content = f"{priority_chunk} {secondary_context}".strip()
            product.save()

        self.stdout.write(self.style.SUCCESS("수수료 소수점 및 LTV 필드 보정 완료."))