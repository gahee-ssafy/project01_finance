#### ai-server-base:v2 python ####
# 1. Miniconda 공식 이미지를 베이스로 선택
FROM continuumio/miniconda3

# 2. 컨테이너 내부용 가상환경 생성 (이름: ai_env_docker)
RUN conda create -n ai_env_docker python=3.10 -y

# 3. 컨테이너 내 기본 실행 환경을 ai_env_docker로 고정
ENV PATH /opt/conda/envs/ai_env_docker/bin:$PATH
ENV CONDA_DEFAULT_ENV=ai_env_docker