FROM python:3.12-slim

# Instalar uv
RUN pip install uv

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copiar dependencias (Usamos uv para instalar sin necesidad de un requirements.txt previo)
COPY . /app/
RUN uv pip install --system django djangorestframework django-cors-headers django-filter drf-spectacular

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]