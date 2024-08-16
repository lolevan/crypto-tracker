# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app

# Копируем файлы с вашего проекта в рабочую директорию контейнера
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения для токенов
ENV TELEGRAM_API_TOKEN=your_telegram_token_here
ENV CMC_API_KEY=your_coinmarketcap_key_here

# Запускаем приложение при старте контейнера
CMD ["python", "app.py"]
