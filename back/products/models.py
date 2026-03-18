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
    # kiwi 전처리없이 진행
    combined_content = models.TextField(null=True, blank=True) 
    combined_embedding = models.JSONField(null=True, blank=True)
    erly_rpay_fee_float = models.FloatField(null=True) # 중도상환수수료 regex 필드 


# 개인신용대출 상품 바구니 
class CreditLoanBaseInfo(models.Model):
    dcls_month = models.CharField(max_length=6)          # 공시 제출월
    fin_co_no = models.CharField(max_length=20)          # 금융회사 코드
    kor_co_nm = models.CharField(max_length=50)          # 금융회사 명
    fin_prdt_cd = models.CharField(max_length=100)       # 금융상품 코드
    fin_prdt_nm = models.CharField(max_length=100)       # 금융 상품명
    join_way = models.TextField()                        # 가입 방법 (분석 시 중요 자격요건 포함됨)
    crdt_prdt_type = models.CharField(max_length=10)     # 대출종류 코드
    crdt_prdt_type_nm = models.CharField(max_length=50)  # 대출종류명 (일반신용, 마이너스통장 등)
    cb_name = models.CharField(max_length=50)            # CB 회사명
    dcls_strt_day = models.CharField(max_length=8)       # 공시 시작일
    dcls_end_day = models.CharField(max_length=8, null=True, blank=True) # 공시 종료일
    fin_co_subm_day = models.CharField(max_length=14)    # 금융회사 제출일
    crdt_lend_rate_type = models.CharField(max_length=10)    # 금리구분 코드
    crdt_lend_rate_type_nm = models.CharField(max_length=50) # 금리구분 (대출금리 등)
    # 점수대별 금리 (null 허용: 해당 점수대 상품이 없을 수 있음)
    crdt_grad_1 = models.FloatField(null=True)   # 900점 초과
    crdt_grad_4 = models.FloatField(null=True)   # 801~900점
    crdt_grad_5 = models.FloatField(null=True)   # 701~800점
    crdt_grad_6 = models.FloatField(null=True)   # 601~700점
    crdt_grad_10 = models.FloatField(null=True)  # 501~600점
    crdt_grad_11 = models.FloatField(null=True)  # 401~500점
    crdt_grad_12 = models.FloatField(null=True)  # 301~400점
    crdt_grad_13 = models.FloatField(null=True)  # 300점 이하
    crdt_grad_avg = models.FloatField(null=True) # 평균 금리
    search_content = models.TextField(null=True, blank=True) # kiwi 전처리된 텍스트
    embedding = models.JSONField(null=True, blank=True) 
    combined_content = models.TextField(null=True, blank=True) 
    combined_embedding = models.JSONField(null=True, blank=True)