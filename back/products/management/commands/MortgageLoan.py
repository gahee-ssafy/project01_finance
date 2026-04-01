import re
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import MortgageBaseInfo

class Command(BaseCommand):
    help = 'API 수집 중 Regex를 통해 중도상환수수료 수치를 추출하여 저장합니다.'

    # 2. 전처리 기계 (Regex Parser)
    def extract_fee_rate(self, text):
        if not text:
            return None
        
        # '면제', '없음' 등의 키워드 포착 시 0.0 반환 -> 3년이후 면세 상품이 있지만 0.0으로 처리됨
        # 따라서 '면제'는 배제함 일괄적으로 3년 이후면 수수료 0임. 
        if any(word in text for word in ['없음']):
            return 0

        # 패턴 설명: 숫자(정수 혹은 소수점 포함) 뒤에 %가 붙은 형태를 찾음
        # 예: "1.2%" -> "1.2" 추출
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None


    help = '금융감독원 API로부터 아파트 담보대출 데이터를 수집하고 저장합니다.'

    def handle(self, *args, **options):
        # 1. API 호출 설정
        api_key = settings.API_KEY
        url = 'http://finlife.fss.or.kr/finlifeapi/mortgageLoanProductsSearch.json'
        
        # 은행(020000) 권역을 기본으로 수집
        params = {
            'auth': api_key,
            'topFinGrpNo': '020000',
            'pageNo': 1
        }

        # 2. 데이터 요청
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            res_json = response.json()
            
            res_data = res_json.get('result', {})
            base_list = res_data.get('baseList', [])
            option_list = res_data.get('optionList', [])
            
            if not base_list:
                self.stdout.write(self.style.WARNING("수집된 데이터가 없습니다."))
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API 호출 중 오류 발생: {e}"))
            return

        # 3. 아파트 담보 옵션 사전 매핑 (O(1) 조회를 위해)
        apt_options = {}
        for opt in option_list:
            if opt.get('mrtg_type_nm') == '아파트':
                cd = opt['fin_prdt_cd']
                # 상품당 하나의 아파트 옵션만 대표로 저장 (상환방식/금리유형 중복 시 첫 번째 것)
                if cd not in apt_options:
                    apt_options[cd] = opt

        # 4. 통합 저장 및 전처리
        updated_count = 0
        created_count = 0

        for base in base_list:
            cd = base['fin_prdt_cd']
            
            # 아파트 담보 옵션이 있는 경우만 진행
            if cd in apt_options:
                opt = apt_options[cd]
                
                # [regex] 저장 직전 전처리
                raw_fee_text = base.get('erly_rpay_fee', '')
                fee_rate = self.extract_fee_rate(raw_fee_text)

                # DB 저장 또는 업데이트
                product, created = MortgageBaseInfo.objects.update_or_create(
                    fin_prdt_cd=cd,
                    defaults={
                        'kor_co_nm': base['kor_co_nm'],
                        'fin_prdt_nm': base['fin_prdt_nm'],
                        'join_way': base.get('join_way', ''),
                        'loan_inci_expn': base.get('loan_inci_expn', ''),
                        'erly_rpay_fee': raw_fee_text,           # 원문 (UI 출력용)
                        'erly_rpay_fee_float': fee_rate,        # 전처리된 수치 (분석용)    
                        'dly_rate': base.get('dly_rate', ''),
                        'loan_lmt': base.get('loan_lmt', ''),
                        'mrtg_type_nm': '아파트',
                        'rpay_type_nm': opt.get('rpay_type_nm'),
                        'lend_rate_type_nm': opt.get('lend_rate_type_nm'),
                        'lend_rate_min': opt.get('lend_rate_min'),
                        'lend_rate_max': opt.get('lend_rate_max'),
                        'lend_rate_avg': opt.get('lend_rate_avg'),
                    }
                )