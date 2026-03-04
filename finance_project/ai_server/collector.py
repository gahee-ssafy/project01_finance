import pandas as pd
from pykrx import stock
from datetime import datetime
import os

def collect_supply_data(target_date):
    # 1. KOSPI 종목 리스트 가져오기
    tickers = stock.get_market_ticker_list(target_date, market="KOSPI")
    
    # 2. 투자자별 순매수량 가져오기 (단위: 주 또는 거래대금 선택 가능)
    # 여기서는 '거래대금' 기준으로 가져옵니다. (단위: 원)
    df = stock.get_market_net_purchases_of_equities_by_ticker(target_date, target_date, "KOSPI")
    
    # 3. 필요한 컬럼만 필터링 (개인, 기관, 외국인)
    df = df[['개인', '기관', '외국인']]
    df['날짜'] = target_date
    df = df.reset_index() # 티커를 컬럼으로 변환
    
    # 4. CSV 저장 (파일이 없으면 새로 만들고, 있으면 아래에 추가)
    file_name = 'kospi_supply_data.csv'
    if not os.path.exists(file_name):
        df.to_csv(file_name, index=False, mode='w', encoding='utf-8-sig')
    else:
        df.to_csv(file_name, index=False, mode='a', header=False, encoding='utf-8-sig')
    
    print(f"{target_date} 데이터 저장 완료.")

# 오늘 날짜로 실행 (장 마감 후 실행 권장)
today = datetime.now().strftime("%Y%m%d")
collect_supply_data(today)