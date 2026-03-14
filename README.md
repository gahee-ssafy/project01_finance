# Finance Project

```


```

---

## 작업 관리

- [해결] 코사인 유사도 검색
- [해결] 데이터베이스 학습: 도커연습(miniconda포함) 기능별 테이블 정리 - 목록 생성시 새로운 테이블로 관리 요망
- [해결] 도커연습 - 이후 colab에서 한 거 도커로 작업할 예정
- [미결] 상관관계
- [미결] 시각화 pandas, matplotlib, seaborn, scikit-learn

---

## 💡 느낀 점/ 보완 점

### 데이터 가공 : 임베딩은 문맥(context)가 중요하다.

1. 프로젝트는 '문서 전체 임베딩' 상태 : 코사인유사도 파악시 노이즈가 많지 않을까? 청킹이 중요하지 않을까?

- kiwi + regex로 중요단어를 포함해 핵심단어 10개로 전처리함.
- 생각보다 유사도가 나오지 않았다.
- 이유는 "문맥을 전달하지 않아 임베딩은 의미를 파악하기 어려움"
- 문맥을 정돈해 전처리 로직을 바꿨다. 유사도가 12%p 상승했다.

### 데이터 시각화

- 개인상품은 요건이 명확하다. 소득이나 신용점수가 있다. 그리고 담보대출도 주택에 치중되어 있어서 정형화된 패턴을 보인다.
- [미결] 기업대출은 요건이 복잡함. 어떻게 할까나~

---

## 프로젝트 개요

- **프로젝트명**: 개인대출 상품 제안
- **설명**: AI 기반 상품 동향을 검토하고 의사결정을 지원하는 금융 서비스
- **기간**: 2026.02.25. ~
- **의문**: 기계가, 개인의 상황에 맞춰 상품을 소개할 수 있을까?

---

## 🏗️기술 스택

### Backend

![Django](https://img.shields.io/badge/Django-092E20.svg?style=for-the-badge&logo=django&logoColor=white)&nbsp;
![Python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)&nbsp;
![sqlite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=SQLite&logoColor=white)&nbsp;

### DevOps

![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)&nbsp;
![Github](https://img.shields.io/badge/Github-000000?style=for-the-badge&logo=github&logoColor=white)&nbsp;

### Tools

![VS code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)&nbsp;
![HuggingFace](https://img.shields.io/badge/huggingface-%23FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=white)&nbsp;

- 추가할 것: torch, '임베딩 모델: Sentence-Transformers', numpy, kiwi
  <br />

---

## [미완] 프로젝트 폴더 구조

project
├── back/ # Django
│ ├── main.py
│ ├── requirements.txt
│ └── models/ # .gitignore에 등록 ([미완]허깅페이스 링크)
└── README.md # 전체 프로젝트 실행 가이드

---

## 데이터 분석 공정

1. 데이터 수집 : 금융감독원API
2. 데이터 처리 및 정제 : 통합 필드를 생성하고 임베딩
3. 데이터 분석 : 유사도가 잘 나오나?
4. 모델링 및 분석 : 코사인 유사도 분석
5. 시각화 :

---

## 환경

- LOCAL KNOWLEDGE BASE:외부 의존성을 최소화하고 로컬 연산

---
