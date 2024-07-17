import asyncio
import logging
import connect

from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# Используйте свой токен
token = '5834123801:AAG1ZyMbaWdafaLle2vryX29P1J0L1iTLyk'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class MyStates(StatesGroup):
    awaiting_response = State()

@dp.message_handler(commands=['start'])
async def start_command(message: Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('🔄Перезагрузить роутер'))
    markup.add(KeyboardButton('👥Показать клиентов'))
    await message.answer('❓Что нужно сделать?', reply_markup=markup)

@dp.message_handler(lambda message: message.text == '🔄Перезагрузить роутер')
async def reboot_router(message: Message):
    connect.off()
    await message.answer('🔄Бот начал перезагружаться! ⏱Ожидайте!')

@dp.message_handler(lambda message: message.text == '👥Показать клиентов')
async def show_clients(message: Message):
    await message.answer(connect.get())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())