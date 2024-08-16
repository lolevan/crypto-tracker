import os
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils import executor

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CMC_API_KEY = os.getenv("CMC_API_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Логирование входящих сообщений
class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        print(f"Received a message: {message.text}")


dp.middleware.setup(LoggingMiddleware())

# Словарь для хранения данных об отслеживаемых валютах и их порогах
tracked_currencies = {}
# Словарь для хранения информации о том, был ли порог уже достигнут
currency_alert_status = {}


# Функция для получения текущего курса криптовалюты
def get_crypto_price(crypto, currency="USD"):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': crypto,
        'convert': currency
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    price = data['data'][crypto]['quote'][currency]['price']
    return price


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я могу отслеживать цены на криптовалюты для тебя. Используй команду /set для задания валюты и пороговых значений.")


# Обработчик команды /set для установки валюты и порогов
@dp.message_handler(commands=['set'])
async def set_currency(message: types.Message):
    args = message.text.split()
    if len(args) != 4:
        await message.reply("Используйте команду в формате: /set <currency> <min_threshold> <max_threshold>")
        return
    currency, min_threshold, max_threshold = args[1].upper(), float(args[2]), float(args[3])
    chat_id = message.chat.id
    tracked_currencies[currency] = (min_threshold, max_threshold, chat_id)
    currency_alert_status[currency] = {'min_reached': False, 'max_reached': False}
    await message.reply(f"Отслеживание {currency} с минимальным порогом {min_threshold} и максимальным порогом {max_threshold} установлено.")


# Фоновая задача для периодического отслеживания курсов
async def track_prices():
    while True:
        for currency, (min_threshold, max_threshold, chat_id) in tracked_currencies.items():
            price = get_crypto_price(currency)
            status = currency_alert_status[currency]

            # Проверка на достижение минимального порога
            if price <= min_threshold and not status['min_reached']:
                await bot.send_message(chat_id, f"{currency} упала ниже минимального порога: {price} USD")
                status['min_reached'] = True  # Обновляем статус, чтобы не отправлять повторные уведомления
                status['max_reached'] = False  # Сбрасываем статус превышения максимального порога

            # Проверка на достижение максимального порога
            elif price >= max_threshold and not status['max_reached']:
                await bot.send_message(chat_id, f"{currency} превысила максимальный порог: {price} USD")
                status['max_reached'] = True  # Обновляем статус, чтобы не отправлять повторные уведомления
                status['min_reached'] = False  # Сбрасываем статус достижения минимального порога

        await asyncio.sleep(60)  # Задержка перед следующей проверкой


# Основной запуск бота
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(track_prices())
    executor.start_polling(dp, loop=loop, skip_updates=True)
