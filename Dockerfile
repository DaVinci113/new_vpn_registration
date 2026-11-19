FROM python:3.13.3-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы манифеста ПЕРВЫМИ (для кэширования слоев Docker)
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости.
# --frozen гарантирует использование uv.lock
RUN uv sync --frozen

# Копируем исходный код приложения
COPY . /app

CMD ["uv", "run", "python", "main.py"]
