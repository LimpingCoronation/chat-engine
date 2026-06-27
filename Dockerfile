FROM python:3.12.3

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python3 -m pip install --upgrade pip
RUN pipx install poetry

COPY . .
RUN poetry install --no-root

EXPOSE 8080
