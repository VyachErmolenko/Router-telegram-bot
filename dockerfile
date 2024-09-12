# Используем базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY src/main.py /app/bot.py

# Устанавливаем зависимости
RUN pip install --no-cache-dir aiogram

# Устанавливаем логирование
ENV LOGLEVEL=info

# Запускаем приложение
CMD ["python", "bot.py"]