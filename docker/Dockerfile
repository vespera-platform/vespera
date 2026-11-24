FROM python:3.12-slim-trixie@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b AS builder
COPY --from=ghcr.io/astral-sh/uv:0.13.4@sha256:9f130421e930bfbdc563c00740466603f8723158e90297d07957c2294640262b /uv /uvx /bin/
WORKDIR /app
COPY . .
RUN uv sync --locked --no-dev

FROM python:3.12-slim-trixie@sha256:191083cdf6c7bda8c76158983163ead5d5cf7b77cf3033e805bb0f5296f51b4b
RUN pip uninstall -y pip
WORKDIR /app
COPY --from=builder /app /app
RUN useradd -u 10001 app
ENV PATH="/app/.venv/bin:$PATH"
ARG GIT_SHA=dev
ENV VESPERA_VERSION=$GIT_SHA
USER 10001
CMD ["uvicorn", "vespera.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]