import pandas as pd
from django.core.management.base import BaseCommand
from products.models import SpotPrice
from django.conf import settings
import os

class Command(BaseCommand):
    help = '금/은 시세 엑셀 데이터를 DB에 저장합니다.'

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        gold_file = os.path.join(base_dir, 'Gold_prices.xlsx')
        silver_file = os.path.join(base_dir, 'Silver_prices.xlsx')

        def load_excel(file_path, item_name):
            try:
                df = pd.read_excel(file_path)
                
                columns = list(df.columns)
                print(f"👀 [{item_name}] 엑셀 컬럼: {columns}")

                # 1. 날짜 컬럼 찾기 ('Date' 우선)
                date_col = None
                for candidate in ['Date', 'date', '일자', '기준일']:
                    if candidate in columns:
                        date_col = candidate
                        break
                
                # 2. 가격 컬럼 찾기 ('Close/Last' 우선)
                price_col = None
                # 캡처해주신 'Close/Last'를 가장 앞에 두었습니다.
                for candidate in ['Close/Last', 'Close', '종가', 'Price', '가격']:
                    if candidate in columns:
                        price_col = candidate
                        break

                if not date_col or not price_col:
                    self.stdout.write(self.style.ERROR(f"❌ {item_name}: 컬럼을 못 찾았습니다. (찾은 날짜: {date_col}, 찾은 가격: {price_col})"))
                    return

                # 3. 데이터 저장
                count = 0
                for index, row in df.iterrows():
                    # 날짜 변환
                    date_val = pd.to_datetime(row[date_col]).date()
                    
                    # 가격 변환 (문자열인 경우 $와 , 제거)
                    price_raw = row[price_col]
                    if isinstance(price_raw, str):
                        price_raw = price_raw.replace('$', '').replace(',', '').strip()
                    
                    price_val = float(price_raw)

                    # 중복 방지
                    if not SpotPrice.objects.filter(base_date=date_val, item_name=item_name).exists():
                        SpotPrice.objects.create(
                            item_name=item_name,
                            base_date=date_val,
                            price=price_val
                        )
                        count += 1
                
                self.stdout.write(self.style.SUCCESS(f'✅ {item_name} {count}건 저장 완료!'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'🔥 {item_name} 에러: {str(e)}'))

        # 파일 실행
        if os.path.exists(gold_file):
            load_excel(gold_file, 'Gold')
        else:
            self.stdout.write(self.style.WARNING(f'파일 없음: {gold_file}'))

        if os.path.exists(silver_file):
            load_excel(silver_file, 'Silver')
        else:
            self.stdout.write(self.style.WARNING(f'파일 없음: {silver_file}'))