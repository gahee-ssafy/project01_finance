from django.db import models

class DepositProducts(models.Model):
    # 금융 상품 코드 (중복 방지를 위한 핵심 키)
    fin_prdt_cd = models.TextField(unique=True) 
    # 금융 회사명 (예: 우리은행)
    kor_co_nm = models.TextField()
    # 상품명 (예: WON플러스 예금)
    fin_prdt_nm = models.TextField()
    # 기타 유의사항
    etc_note = models.TextField()
    # 가입 대상 (실명, 제한없음 등)
    join_deny = models.IntegerField() 
    # 가입 방법 (인터넷, 스마트폰 등)
    join_way = models.TextField() 
    # 우대 조건
    spcl_cnd = models.TextField()

    # [F09] 추가: AI가 만든 숫자를 저장할 공간!
    embedding_vector = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.fin_prdt_nm


class DepositOptions(models.Model):
    # 어떤 상품의 옵션인지 (ForeignKey)
    product = models.ForeignKey(DepositProducts, on_delete=models.CASCADE, related_name='options')
    # 금융 상품 코드 (API 응답 데이터와 매핑용)
    fin_prdt_cd = models.TextField()
    # 저축 금리 유형 (S: 단리, M: 복리)
    intr_rate_type_nm = models.CharField(max_length=100)
    # 저축 금리 (기본 금리)
    intr_rate = models.FloatField(null=True) 
    # 최고 우대 금리
    intr_rate2 = models.FloatField(null=True)
    # 저축 기간 (6, 12, 24, 36개월)
    save_trm = models.IntegerField()

    def __str__(self):
        return f"{self.product.fin_prdt_nm} - {self.save_trm}개월"
    

class SpotPrice(models.Model):
    # 금(Gold) 또는 은(Silver) 구분
    item_name = models.CharField(max_length=10)
    # 기준 날짜
    base_date = models.DateField()
    # 가격 (소수점 포함 가능성 대비 FloatField, 혹은 정수라면 IntegerField)
    price = models.FloatField()

    def __str__(self):
        return f"{self.item_name} - {self.base_date}"
    