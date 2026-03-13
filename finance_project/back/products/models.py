from django.db import models

class MortgageBaseInfo(models.Model):
    fin_prdt_cd = models.CharField(max_length=100, unique=True) # 상품 코드
    kor_co_nm = models.CharField(max_length=100)               # 금융 회사명
    fin_prdt_nm = models.CharField(max_length=100)              # 상품명
    join_way = models.TextField(null=True, blank=True)          # 가입 방법
    loan_inci_expn = models.TextField(null=True, blank=True)    # 대출 부대비용
    erly_rpay_fee = models.TextField(null=True, blank=True)     # 중도상환수수료
    dly_rate = models.TextField(null=True, blank=True)          # 연체 이자율
    loan_lmt = models.TextField(null=True, blank=True)          # 대출 한도
    mrtg_type_nm = models.CharField(max_length=100, default='아파트')            # 담보 유형 (예: 아파트, 단독주택)
    rpay_type_nm = models.CharField(max_length=100)            # 상환 방식 (예: 원리금분할상환)
    lend_rate_type_nm = models.CharField(max_length=100)       # 금리 유형 (예: 고정금리, 변동금리)
    lend_rate_min = models.FloatField(null=True)               # 최저 금리
    lend_rate_max = models.FloatField(null=True)               # 최고 금리
    search_content = models.TextField(null=True, blank=True) # kiwi 전처리된 텍스트
    embedding = models.JSONField(null=True, blank=True)
