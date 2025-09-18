# 1. 베이스 이미지
FROM python:3.13-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 시스템 의존성 설치 (PostgreSQL client 등)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 4. requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 앱 코드 복사
COPY . .

# 6. 포트 노출
EXPOSE 8000

# 7. 서버 실행 명령
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]