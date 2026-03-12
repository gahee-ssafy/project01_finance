import re
from django.core.management.base import BaseCommand
from products.models import MortgageBaseInfo
from kiwipiepy import Kiwi

class Command(BaseCommand):
    help = '원시 데이터를 참조하여 공통점과 차별점(수치)을 모두 담은 검색 필드를 생성합니다.'

    kiwi = Kiwi()
    # 금융 도메인에서 변별력이 없는 공통 노이즈 단어
    STOPWORDS = {'인지세', '채권', '매입', '근저당권', '설정', '비용', '확인', '제공', '부담', '대상', '관련'}

    def extract_values(self, text):
        """정규표현식으로 LTV와 % 수치를 정밀 타격하여 추출 (영점 조절)"""
        if not text: return ""
        # 1. LTV 00% 또는 00% 형태의 수치 추출
        ltv_match = re.search(r'(LTV\s?\d{1,3}%?|\d{1,2}%(?=\s?이내))', text)
        # 2. 0.0% 형태의 수수료율 추출
        rate_match = re.findall(r'\d?\.?\d{1,2}%', text)
        
        results = []
        if ltv_match: results.append(ltv_match.group(0))
        if rate_match: results.extend(rate_match)
        
        return " ".join(list(dict.fromkeys(results)))

    def clean_context(self, text):
        """조사 제거 및 핵심 명사 추출 (최대 10개 제한)"""
        if not text: return ""
        res = self.kiwi.analyze(text)
        
        # 1. 태그 필터링 및 불용어 제거
        tokens = []
        for result, score in res:
            for token in result:
                if token.tag in ['NNG', 'NNP', 'SL']:
                    if token.form not in self.STOPWORDS and len(token.form) > 1:
                        tokens.append(token.form)
        
        # 2. 중복 제거 (순서 유지)
        unique_tokens = []
        for t in tokens:
            if t not in unique_tokens:
                unique_tokens.append(t)
        
        # 3. ⚠️ 핵심 영점 조절: 상위 10개 단어만 슬라이싱
        limited_tokens = unique_tokens[:10]
        
        return " ".join(limited_tokens)

    def handle(self, *args, **options):
        # search_content가 비어있는 원시 데이터들을 타겟팅
        targets = MortgageBaseInfo.objects.all()
        self.stdout.write(f"총 {targets.count()}개의 원시 데이터 참조 시작...")

        updated_count = 0
        for product in targets:
            # 1. 원시 데이터 참조
            raw_inci = product.loan_inci_expn or ""
            raw_fee = product.erly_rpay_fee or ""
            raw_name = product.fin_prdt_nm
            
            # 2. 차별점 추출 (수치 영점 조절)
            refined_values = self.extract_values(raw_inci + " " + raw_fee)
            
            # 3. 공통점 추출 (Kiwi 문맥)
            refined_context = self.clean_context(raw_name + " " + raw_inci)
            
            # 4. 필드 결합 (차별점[수치]을 앞쪽에 배치하여 검색 가중치 부여)
            product.search_content = f"[{refined_values}] {refined_context}".strip()
            product.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"성공적으로 {updated_count}개의 데이터 영점을 조절하여 저장했습니다."))
