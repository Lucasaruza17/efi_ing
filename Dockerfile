FROM python:3.12-slim

# uv (gestor de entornos y dependencias) desde su imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# El entorno virtual vive fuera de /app para que el volumen del docker-compose no lo tape
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Primero las dependencias, así Docker reutiliza la capa si no cambian
COPY pyproject.toml uv.lock* .python-version ./
RUN uv sync --no-install-project

# Después el código
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
