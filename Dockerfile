# Imagen base de Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements e instalarlos
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Exponer el puerto del servidor
EXPOSE 8000

# Comando para correr la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
