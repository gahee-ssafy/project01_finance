# [Layer 1] 베이스 이미지 (이미 찍혀 있음)
FROM continuumio/miniconda3

WORKDIR /app

# [Layer 2] 무거운 환경 설정만 먼저 복사 (캐시 활용의 핵심)
# 이 파일이 안 바뀌면 아래의 무거운 설치 과정은 통째로 건너뜁니다.
COPY environment.yml .
RUN conda env create -f environment.yml && conda clean -afy

# [Layer 3] 환경 활성화 설정 (거의 안 바뀜)
ENV PATH /opt/conda/envs/ai_env/bin:$PATH
SHELL ["conda", "run", "-n", "ai_env", "/bin/bash", "-c"]

# [Layer 4] 실제 소스 코드 (가장 마지막에 복사!)
# 이제 코드 한 줄 고쳐도 위쪽의 무거운 설치 과정을 다시 하지 않습니다.
COPY . .

CMD ["python", "backend/collector.py"]