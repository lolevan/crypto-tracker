import os
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils import executor

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
CMC_API_KEY = os.getenv("CMC_API_KEY")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        print(f"Received a message: {message.text}")


dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я могу отслеживать цены на криптовалюты для тебя. Используй команду /set для задания валюты и пороговых значений.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
