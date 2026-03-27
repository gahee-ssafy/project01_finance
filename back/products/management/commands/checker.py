import os
import certifi  
import torch
from sentence_transformers import SentenceTransformer, util

os.environ['SSL_CERT_FILE'] = certifi.where()

class LoanEligibilityChecker:
    def __init__(self):
        # SBERT 모델 로드 (사용자님 기보유 모델)
        self.model = SentenceTransformer('jhgan/ko-sroberta-multitask')

    def analyze(self, user_query, user_profile):
        """
        함수 내부에 규정 데이터를 포함
        TODO: 어디 사에서 가져오느냐에 따라 값이 다를 것임. 현재는 예시로 하드코딩
        """
        # 1. 통합 규정
        mortgage_rules = [
            {
                "description": "서울특별시 및 투기과열지구 내 아파트 담보대출 규정",
                "ltv_ratio": 0.5,
                "room_deduction": 55000000,
                "region": "서울"
            },
            {
                "description": "경기도 및 광역시 일반 지역 주택담보대출 규정",
                "ltv_ratio": 0.7,
                "room_deduction": 28000000,
                "region": "경기/광역시"
            },
            {
                "description": "기타지역 주택 구입자 대상 우대 LTV 규정",
                "ltv_ratio": 0.7,
                "room_deduction": 25000000,
                "region": "기타 지역"
            }
        ]

        # 2. SBERT 의미론적 유사도 검색
        rule_descriptions = [r['description'] for r in mortgage_rules]
        rule_embeddings = self.model.encode(rule_descriptions, convert_to_tensor=True)
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        
        cos_scores = util.cos_sim(query_embedding, rule_embeddings)[0]
        best_idx = torch.argmax(cos_scores).item()
        matched_rule = mortgage_rules[best_idx]

        # 3. 정량적 LTV 산술 연산
        # 산식: (집값 * LTV비율) - 방공제
        ltv = matched_rule['ltv_ratio']
        deduction = matched_rule['room_deduction']
        house_value = user_profile.get('house_price', 0)
        
        calculated_limit = (house_value * ltv) - deduction
        final_limit = max(0, int(calculated_limit))

        # 4. 분석 결과 도출
        return {
            "applied_rule": matched_rule['description'],
            "confidence": f"{float(cos_scores[best_idx])*100:.2f}%",
            "calculation_detail": {
                "ltv": f"{int(ltv*100)}%",
                "deduction": f"{deduction:,}원",
                "max_loan": f"{final_limit:,}원"
            },
            "msg": f"은행원 모드: 분석 결과 {matched_rule['region']} 기준으로 "
                   f"최대 {final_limit:,}원까지 대출이 가능할 것으로 예상됩니다."
                   f"LTV {int(ltv*100)}% 적용하며, 방공제 {deduction:,}원입니다."
                   f"또한, 생애최초인 경우는 방공제 이전 금액을 기준으로 10%p 추가 대출 가능합니다. 참고하시기 바랍니다."
        }
# --- 실행 테스트 ---
if __name__ == "__main__":
    checker = LoanEligibilityChecker()
    # TODO: user_info: 10억 아파트 가정
    # 해당 수치는 필수입력값
    user_info = {"house_price": 1000000000} 
    # result = checker.analyze("나 서울에 10억짜리 아파트 사는데 대출 한도 알려줘", user_info)
    result = checker.analyze("진주에 아파트 살려고 대출 한도 알려줘", user_info)
    print(result['msg'])