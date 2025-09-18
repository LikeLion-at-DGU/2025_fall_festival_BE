# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 빌드 의존성(필요시만) 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

# non-root user
RUN useradd --create-home appuser
RUN mkdir /app && chown appuser:appuser /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Optional: entrypoint.sh 를 통해 collectstatic/migrate 제어 가능 (아래 예시 제공)
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "project.wsgi:application", "--workers", "3", "--threads", "2", "--bind", "0.0.0.0:8000"]
