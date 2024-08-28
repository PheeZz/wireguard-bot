FROM python:3.10.14-slim-bookworm

ENV LANG=C.UTF-8
ENV DB_USER=wireguard_user
ENV DB_PASS=postgres
ENV DB_NAME=wireguard_bot
ENV DB_HOST=db
ENV DB_PORT=5433
ENV VIRTUAL_ENV_DISABLE_PROMPT=1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV AM_I_IN_A_DOCKER_CONTAINER=Yes
ENV DOCKER_BUILDKIT=1

RUN apt update && apt install -y curl iptables wireguard

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install packaging && \
    pip install poetry


# add requirements to the image
COPY poetry.lock pyproject.toml /app/

# Install dependencies to system without creating virtual environment
RUN poetry install --no-interaction --no-ansi --no-root

# add all parent directory to the image
ADD . /app