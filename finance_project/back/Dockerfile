FROM python:3.10

# 1. 작업 디렉토리 설정
WORKDIR /code

# 2. 의존성 파일 복사 및 설치 (psycopg2-binary 필수!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 소스 코드 전체 복사
COPY . .

