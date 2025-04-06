FROM python:3.11-slim

WORKDIR /app

# Poetry 설치 및 설정
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && pip install poetry \
  && poetry config virtualenvs.create false \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="${PATH}:/root/.local/bin"

# pyproject.toml 복사 및 패키지 설치
COPY pyproject.toml /app
COPY poetry.lock* /app/
RUN poetry install --no-root

# 소스코드 전체 복사
COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]


