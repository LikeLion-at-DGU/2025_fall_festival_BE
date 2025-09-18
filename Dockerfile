# Dockerfile
FROM python:3.13-slim

# Python 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리
WORKDIR /app

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

# requirements 설치
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# entrypoint.sh 있으면 실행 (없으면 CMD 바로 실행됨)
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "project.wsgi:application", "--workers", "3", "--threads", "2", "--bind", "0.0.0.0:8000"]
