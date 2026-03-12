import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import MortgageBaseInfo

class Command(BaseCommand):
    help = '금융감독원 API로부터 주택담보대출 데이터를 수집하여 통합 DB에 저장합니다.'

    def handle(self, *args, **options):
        # 1. API 설정
        api_key = settings.API_KEY 
        url = 'http://finlife.fss.or.kr/finlifeapi/mortgageLoanProductsSearch.json'
        params = {
            'auth': api_key,
            'topFinGrpNo': '020000', # 은행 권역
            'pageNo': 1
        }

        # 2. 데이터 요청
        try:
            response = requests.get(url, params=params).json()
            res_data = response.get('result', {})
            base_list = res_data.get('baseList', [])
            option_list = res_data.get('optionList', [])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"조회 실패: {e}"))
            return

        # 3. 아파트 옵션 정보 사전 정리 (기계적 매핑)
        # 같은 상품 코드(fin_prdt_cd)에 여러 옵션이 있을 경우 첫 번째 '아파트' 옵션만 추출
        apt_options = {}
        for opt in option_list:
            if opt.get('mrtg_type_nm') == '아파트':
                cd = opt['fin_prdt_cd']
                if cd not in apt_options:
                    apt_options[cd] = opt

        # 4. 데이터 통합 저장
        count = 0
        for base in base_list:
            cd = base['fin_prdt_cd']
            
            # 아파트 옵션이 존재하는 상품만 저장
            if cd in apt_options:
                opt = apt_options[cd]
                
                # 임베딩을 위한 기초 텍스트 조합
                combined_text = f"{base['fin_prdt_nm']} {base.get('kor_co_nm', '')} {opt.get('lend_rate_type_nm', '')} {base.get('loan_inci_expn', '')}"

                product, created = MortgageBaseInfo.objects.update_or_create(
                    fin_prdt_cd=cd, # 👈 유일한 식별자
                    defaults={
                        'kor_co_nm': base['kor_co_nm'],
                        'fin_prdt_nm': base['fin_prdt_nm'],
                        'join_way': base['join_way'],
                        'loan_inci_expn': base.get('loan_inci_expn', ''),
                        'erly_rpay_fee': base.get('erly_rpay_fee', ''),
                        'dly_rate': base.get('dly_rate', ''),
                        'loan_lmt': base.get('loan_lmt', ''),
                        'mrtg_type_nm': '아파트',
                        'rpay_type_nm': opt.get('rpay_type_nm'),
                        'lend_rate_type_nm': opt.get('lend_rate_type_nm'),
                        'lend_rate_min': opt.get('lend_rate_min'),
                        'lend_rate_max': opt.get('lend_rate_max'),
                        'search_content': combined_text,
                    }
                )
                if created:
                    self.stdout.write(f"신규 아파트 상품 등록: {product.fin_prdt_nm}")
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'총 {count}개의 아파트 담보대출 데이터 동기화 완료!'))