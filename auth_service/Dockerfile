# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR ./

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем все остальные файлы проекта в рабочую директорию
COPY . .

# Устанавливаем переменные окружения для Python
ENV PYTHONUNBUFFERED 1

# Команда для запуска приложения
#CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--log-level", "warning"]
#CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "debug:app", "--bind", "0.0.0.0:8000", "--log-level", "warning"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
CMD ["python", "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]