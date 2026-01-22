FROM python:3.11-slim-bookworm

RUN pip install uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1 UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]