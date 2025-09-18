FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--workers", "3", "--threads", "2", "project.wsgi:application", "--bind", "0.0.0.0:8000"]