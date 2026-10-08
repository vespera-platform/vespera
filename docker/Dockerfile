FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --locked --no-dev
RUN useradd -u 10001 app
USER 10001
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "vespera.api.main:app", "--host", "0.0.0.0", "--port", "8000"]