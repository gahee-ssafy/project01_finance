# Finance Project
# 프론트는 전체 리팩토링 예정. 레퍼런스 하나 잡아서 그대로 구현할 예정 
# 백엔드 프로젝트 구조, accounts에서 urls, models, serializer, views 구현함. 

---

## 향후 개선 방향

- [미결] 코사인 유사도 검색
- [해결] 데이터베이스 학습: 기능별 테이블 정리 - 목록 생성시 새로운 테이블로 관리 요망
- [미결] 도커연습 - 이후 colab에서 한 거 도커로 작업할 예정

---

## 프로젝트 개요

- **프로젝트명**: 주가반영 금융 의사결정 지원 웹 
- **설명**: AI 기반 상품 동향을 검토하고 의사결정을 지원하는 금융 서비스
- **기간**: 2025.12.19. ~ 2025.12.26.
- **보완기간**: 2026.02.25. ~

---

### 문제 상황

- 상품이 많아 선택이 어려움 : TOP 3 select 지원 
- ROE, 거래현황, 투자성향 등 요건이 다양함. : 주요 기능  

### 타겟 사용자

- 국내시장 개인 투자자
- 국내시장 외국인 투자자
- 국내시장 기관 투자자  

---
## API명세서
![API명세서](./API명세서.png)

## ERD

![ERD](./ERD.png)

---

<br />

## 🏗️기술 스택

### Backend

![Django](https://img.shields.io/badge/Django-092E20.svg?style=for-the-badge&logo=django&logoColor=white)&nbsp;
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)&nbsp;
![postgresql](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)&nbsp;

### Frontend

![Vue.js](https://img.shields.io/badge/vue.js-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)&nbsp;

### DevOps

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)&nbsp;
![Github](https://img.shields.io/badge/Github-000000?style=for-the-badge&logo=github&logoColor=white)&nbsp;

### Tools

![VS code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)&nbsp;
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)&nbsp;

<br />

---

## [미완] 프로젝트 폴더 구조

### Backend (Django)

```
backend
├─ accounts
├─ community
├─ products
├─ mypage
└─ project
```

### Frontend (Vue)

```
frontend
├─ public
└─ src
    ├─ assets
    ├─ components
    ├─ router
    ├─ stores
    └─ views
        ├─ community
        ├─ youtube
        └─ etc
```

---

## 기능

1. 회원가입 및 로그인, 로그아웃 기능
2. 게시글 작성 기능
3. 게시글 및 상품 찜 기능
4. AI 상품 추천

- 사용자 입력을 임베딩하여 상품 벡터와 유사도 계산
- 코사인 유사도 기반 상위 3개 상품 추천
- 추천 상품별 최고 우대 금리 제공
- `prefetch_related`를 활용한 DB 성능 최적화

![다이어그램_추천기능](https://github.com/user-attachments/assets/1d181bae-2210-47a6-967b-f385346f2209) <br>
`back\products\management\commands\get_deposit_products.py` <br>
`back\products\views.py\recommend`

---

## 학습 내용

- Django REST Framework와 Vue.js 연동 구조 이해
- 프론트엔드–백엔드 데이터 흐름 설계 경험
- LOCAL KNOWLEDGE BASE:외부 의존성을 최소화하고 로컬 연산

---

## 💡 느낀 점/ 보완 점

1. 로컬 연산으로 처리 속도 확보.
   - prefetch_related가 없었다면 발생했을 비효율을 계산해 보면 차이가 명확합니다.
   - 미사용: 38번의 DB 통신 ;
     - 상품 목록 조회 1번 + 각 상품의 금리를 찾기 위한 개별 조회 37번
   - 사용: 2번의 DB 통신 ; 상품 목록 조회 1번 + 모든 금리 옵션 일괄 조회 1번

   - [결론] : DB 서버와 통신할 때 네트워크 시간이 걸립니다. 또는 네트워크 문제로 외부 데이터를 가져올 때 시간지연의 애로사항이 있습니다. 이 횟수를 줄이는 것 만으로도 성능이 향상되고 처리 속도가 빨라집니다

2. 데이터 청킹 보완 필요.
   - 청킹은 긴 텍스트를 AI가 이해하기 좋은 '의미 단위'로 나누는 과정이나, 해당 부분에서 더블체크를 놓쳤습니다. views.py에서 유사도를 계산할 때 로그를 찍어보며 청킹의 필요성을 느껴보려 합니다. 혹은 테스트를 통해서 결과를 비교하는 과정도 방법입니다. 다만, 현재 deposit 임베딩 데이터는 상품정보의 우대조건을 다뤘기에 데이터의 질의 부분에서 어느정도 확보가 된 상태라고 생각합니다.
