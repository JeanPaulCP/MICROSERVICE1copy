FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre la app
EXPOSE 8000

CMD ["fastapi", "dev", "main.py"]