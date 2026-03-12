import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import MortgageBaseInfo

class Command(BaseCommand):
    help = '금융감독원 API로부터 아파트 담보대출 데이터를 수집하고 Kiwi로 전처리하여 저장합니다.'

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
                
                # DB 저장 또는 업데이트
                product, created = MortgageBaseInfo.objects.update_or_create(
                    fin_prdt_cd=cd,
                    defaults={
                        'kor_co_nm': base['kor_co_nm'],
                        'fin_prdt_nm': base['fin_prdt_nm'],
                        'join_way': base.get('join_way', ''),
                        'loan_inci_expn': base.get('loan_inci_expn', ''),
                        'erly_rpay_fee': base.get('erly_rpay_fee', ''),
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