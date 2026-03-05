#### AI 개발 환경 통합 패키지 (Python 3.10 + AI Libs) ####

# 1. 베이스 이미지: 파이썬 3.10이 설치된 가벼운 리눅스(slim)를 사용합니다.
FROM python:3.10

ENV PATH="/usr/local/bin:${PATH}"

# 3. 작업 디렉토리 설정 (컨테이너 접속 시 바로 /app 폴더로 들어갑니다)
WORKDIR /app

# 4. 무거운 AI 패키지들 한 번에 설치 (레이어 최적화)
# pandas, numpy, pykrx 등 필요한 패키지를 여기에 나열하세요.
RUN pip install --no-cache-dir \
    pandas \
    pykrx 

# 6. 기본 실행 명령 (파이썬 쉘 실행)
CMD ["python"]