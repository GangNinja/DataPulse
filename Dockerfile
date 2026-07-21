FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY . .

RUN mkdir -p logs reports \
    && useradd --create-home --shell /bin/bash datapulse \
    && chown -R datapulse:datapulse /app

USER datapulse

EXPOSE 8501

CMD ["python", "main.py"]
