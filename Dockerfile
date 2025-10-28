# proyecto-notifications/Dockerfile
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && python -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# crear usuario no-root
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Añadir --proxy-headers cuando hay proxy/ALB delante
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
