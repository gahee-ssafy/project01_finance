import pandas as pd
from pykrx import stock
print("--- 라이브러리 로드 완료 ---")

# 샘플 데이터 수집 시도
try:
    print("삼성전자(005930) 데이터 요청 중...")
    df = stock.get_market_trading_value_by_date("20210115", "20210122", "005930")
    
    if df.empty:
        print("결과: 데이터가 비어 있습니다 (Empty DataFrame)")
    else:
        print("결과: 데이터 수집 성공!")
        print(df.head())
except Exception as e:
    print(f"기계적 오류 발생: {e}")