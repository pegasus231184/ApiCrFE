FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de aplicación
COPY . .

# Cambiar permisos
RUN chown -R app:app /app

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]