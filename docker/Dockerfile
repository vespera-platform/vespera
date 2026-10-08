FROM python:3.12-slim AS builder
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --locked --no-dev

FROM python:3.12-slim
RUN pip uninstall -y pip
WORKDIR /app
COPY --from=builder /app /app
RUN useradd -u 10001 app
ENV PATH="/app/.venv/bin:$PATH"
USER 10001
CMD ["uvicorn", "vespera.api.main:app", "--host", "0.0.0.0", "--port", "8000"]