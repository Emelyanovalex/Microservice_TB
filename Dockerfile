FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn python-dotenv requests

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4321"]
