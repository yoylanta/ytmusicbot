import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from pytubefix import YouTube
from urllib.parse import urlparse, parse_qs
from aiogram.types import FSInputFile


load_dotenv()

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_BOT_API_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне ссылку на видео YouTube, и я загружу аудио.")
@dp.message()
async def download_audio(message: types.Message):
    url = message.text
    await message.reply("Загружаю аудио...")

    parsed_url = urlparse(url)
    if parsed_url.hostname not in ["www.youtube.com", "youtube.com", "youtu.be"]:
        await message.reply("Пожалуйста, отправьте корректную ссылку на YouTube.")
        return
    
    try:
        logging.info(f"Обрабатываем видео: {url}")
        yt = YouTube(url)
        print(yt.title)
        logging.info(f"Получен объект YouTube для: {yt.title}")  # Логируем заголовок видео
        if yt.age_restricted:
            await message.reply("Это видео ограничено по возрасту.")
            return

        audio_stream = yt.streams.filter(only_audio=True).first()

        if not audio_stream:
            await message.reply("Извините, не удалось найти доступные аудиотреки.")
            return

        file_path = audio_stream.download(filename=f"{yt.title}.mp4")

        await bot.send_audio(message.chat.id, FSInputFile(file_path), caption=yt.title)
        await message.reply("Аудио успешно загружено!")

        # Удаляем файл после успешной отправки
        os.remove(file_path)
        logging.info(f"Файл {file_path} успешно удален после отправки.")

    except Exception as e:
        logging.error(f"Ошибка при загрузке аудио: {e}")
        await message.reply(f"Произошла ошибка: {str(e)}")



async def start_bot():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_bot())
