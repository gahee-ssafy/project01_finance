from pykrx import stock
import datetime

df = stock.get_market_ohlcv("20210122", "KOSPI")
print(df.head(3))
