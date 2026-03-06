from pykrx import stock
import datetime

# 최근 영업일 데이터를 안전하게 가져오기 위해 날짜 설정
# (오늘 데이터가 없을 경우를 대비해 어제 날짜 등 명시적 날짜 권장)
target_date = "20251211" 

try:
    # 티커 리스트 가져오기
    tickers = stock.get_market_ticker_list(target_date, market="KOSPI")
    print(f"리스트 가져오기: {len(tickers)}")
    # DataFrame인지 확인하고 비어있는지 체크
    if len(tickers) == 0:
        print(f"{target_date}에 해당하는 데이터가 없습니다. 휴장일인지 확인하세요.")
    else:
        print(f"조회 성공! 티커 개수: {len(tickers)}")
        print(tickers[:5])

except Exception as e:
    print(f"실행 중 오류 발생: {e}")