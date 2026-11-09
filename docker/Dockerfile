FROM python:3.12-slim-trixie@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54 AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.4@sha256:9f130421e930bfbdc563c00740466603f8723158e90297d07957c2294640262b /uv /uvx /bin/
WORKDIR /app
COPY . .
RUN uv sync --locked --no-dev

FROM python:3.12-slim-trixie@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*
RUN pip uninstall -y pip
WORKDIR /app
COPY --from=builder /app /app
RUN useradd -u 10001 app
ENV PATH="/app/.venv/bin:$PATH"
ARG GIT_SHA=dev
ENV VESPERA_VERSION=$GIT_SHA
USER 10001
CMD ["uvicorn", "vespera.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]