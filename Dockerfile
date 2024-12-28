FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/backend

CMD ["gunicorn", "--workers 2 --bind", "0.0.0.0:7001", "server:app"]