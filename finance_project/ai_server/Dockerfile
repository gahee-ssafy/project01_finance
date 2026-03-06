#### [pykrx 환경] ####

# 1. 베이스 이미지: 파이썬 3.10이 설치된 가벼운 리눅스(slim)를 사용합니다.
FROM python:3.10

# python 버전 관련 경로  
ENV PATH="/usr/local/bin:${PATH}"

# 3. 작업 디렉토리 설정 (컨테이너 접속 시 바로 /app 폴더로 들어갑니다)
WORKDIR /app

# [오류] pip 자체를 최신으로 업데이트하고 빌드 도구를 먼저 설치
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. 무거운 AI 패키지들 한 번에 설치 
# pandas, numpy, pykrx 등 필요한 패키지를 여기에 나열하세요.
RUN pip install --no-cache-dir \
    "requests==2.32.0"\
    "pandas==2.2.0"\
    "numpy==1.24.0"\
    "deprecated==1.2.14"\
    "multipledispatch==1.0.0"\
    "matplotlib==3.8.0"\
    "pykrx"

# 6. 기본 실행 명령 (파이썬 쉘 실행)
CMD ["python"]
