FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt -r test-requirements.txt

RUN pip install pre-commit && pre-commit install-hooks

EXPOSE 8000

CMD ["pytest", "test/", "--asyncio-mode=auto", "--disable-warnings", "-v"]
