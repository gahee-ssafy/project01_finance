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

class ManualChunk(models.Model):
    # 매뉴얼 텍스트
    content = models.TextField()
    
    # SBERT 모델로 생성한 고차원 벡터 (바이너리 저장)
    embedding = models.BinaryField()
    
    # 출처 및 페이지 정보 (근거 제시용)
    chapter_title = models.CharField(max_length=200, null=True)
    page_number = models.IntegerField(null=True)
    
    def __str__(self):
        return f"{self.chapter_title} - {self.page_number}p"
    