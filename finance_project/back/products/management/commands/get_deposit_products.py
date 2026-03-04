import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import DepositProducts, DepositOptions

class Command(BaseCommand):
    help = '금융감독원 API로부터 정기예금 데이터를 수집하여 DB에 저장합니다.'

    def handle(self, *args, **options):
        # 1. API URL 및 키 설정
        api_key = settings.FINLIFE_API_KEY # settings.py에 .env 연동 필요
        url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1'

        # 2. 데이터 요청
        response = requests.get(url).json()
        
        # 👇 [추가] API가 도대체 뭐라고 대답했는지 눈으로 확인해봅시다!
        print("---------------- API 응답 데이터 ----------------")
        print(response)
        print("------------------------------------------------")

        
        # 3. 응답 데이터 파싱
        base_list = response['result']['baseList']   # 상품 기본 정보
        option_list = response['result']['optionList'] # 상품 옵션 정보

        # 4. 상품 기본 정보 저장 (중복 방지: save_product 함수로 분리 추천)
        for base in base_list:
            # 이미 존재하는 상품인지 확인 (fin_prdt_cd 기준)
            if DepositProducts.objects.filter(fin_prdt_cd=base['fin_prdt_cd']).exists():
                continue # 이미 있으면 건너뜀 (나중에는 업데이트 로직으로 변경 가능)

            product = DepositProducts(
                fin_prdt_cd=base['fin_prdt_cd'],
                kor_co_nm=base['kor_co_nm'],
                fin_prdt_nm=base['fin_prdt_nm'],
                etc_note=base['etc_note'],
                join_deny=int(base['join_deny']),
                join_way=base['join_way'],
                spcl_cnd=base['spcl_cnd']
            )
            product.save()

        # 5. 옵션 정보 저장
        for option in option_list:
            # 해당 옵션의 부모 상품을 DB에서 찾음
            try:
                product = DepositProducts.objects.get(fin_prdt_cd=option['fin_prdt_cd'])
            except DepositProducts.DoesNotExist:
                # 상품 정보가 없으면 옵션도 저장 불가
                continue
            
            # 옵션 중복 저장 방지 (상품 + 기간 + 금리유형이 같으면 중복으로 간주)
            if DepositOptions.objects.filter(
                product=product, 
                save_trm=int(option['save_trm']), 
                intr_rate_type_nm=option['intr_rate_type_nm']
            ).exists():
                continue

            # intr_rate가 None인 경우 처리 (API 데이터에 null이 있을 수 있음)
            rate = option['intr_rate'] if option['intr_rate'] is not None else -1
            rate2 = option['intr_rate2'] if option['intr_rate2'] is not None else -1

            DepositOptions.objects.create(
                product=product,
                fin_prdt_cd=option['fin_prdt_cd'],
                intr_rate_type_nm=option['intr_rate_type_nm'],
                intr_rate=rate,
                intr_rate2=rate2,
                save_trm=int(option['save_trm'])
            )

        self.stdout.write(self.style.SUCCESS('정기예금 데이터 수집 완료!'))