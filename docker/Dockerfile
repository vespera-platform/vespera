FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --locked --no-dev
CMD ["uv", "run", "uvicorn", "vespera.api.main:app", "--host", "0.0.0.0", "--port", "8000"]