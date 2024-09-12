import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from datetime import datetime, timedelta
import telnetlib
import asyncio

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = '6992865648:AAFuuAQAJnnBtIQp8xxSdKUhlZrQ3CKBZ5A'  # Замените на ваш токен
ROUTER_IP = '1may43a.keenetic.link'  # IP вашего роутера
ROUTER_USERNAME = 'operator'  # Имя пользователя для доступа к роутеру
ROUTER_PASSWORD = 'MfUa2024'  # Пароль для доступа к роутеру

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Данные клиентов
clients = {
    '+79772771189': {
        'paid_until': datetime.now() + timedelta(days=30),  # Доступ на месяц
        'mac': '22:37:0e:be:10:c',
        'ip': '192.168.1.41',
    },
    '+79067144672': {
        'paid_until': datetime.now() + timedelta(days=30),  # Доступ на месяц
        'mac': '78:b2:13:c8:8f:fb',
        'ip': '192.168.1.45',
    },
}

class MenuStates(StatesGroup):
    main_menu = State()
    check_time = State()
    payment = State()

# Функция проверки времени доступа клиентов
async def check_access_status():
    while True:
        current_time = datetime.now()
        for phone, client in clients.items():
            if client['paid_until'] <= current_time:
                # Если время доступа истекло, блокируем доступ
                await block_access(client['ip'], client['mac'])
                logging.info(f"Доступ для клиента {phone} заблокирован.")
        await asyncio.sleep(60)  # Проверяем каждую минуту

# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await return_to_main_menu(message)

# Обработка выбора проверки времени
@dp.message_handler(text="Проверить время", state=MenuStates.main_menu)
async def handle_check_time(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = list(clients.keys())
    keyboard.add(*buttons)
    await message.answer("Выберите номер телефона:", reply_markup=keyboard)
    await MenuStates.check_time.set()

# Обработка выбора номера для проверки времени
@dp.message_handler(state=MenuStates.check_time)
async def check_time(message: types.Message, state: FSMContext):
    phone = message.text
    if phone in clients:
        paid_until = clients[phone]['paid_until']
        remaining_time = paid_until - datetime.now()
        if remaining_time.total_seconds() > 0:
            await message.answer(
                f"Время доступа для номера {phone} истекает через {remaining_time.days} дней и {remaining_time.seconds // 3600} часов.")
        else:
            await message.answer(f"Доступ для номера {phone} истек. Необходимо произвести оплату.")
            # Блокируем доступ
            await block_access(clients[phone]['ip'], clients[phone]['mac'])
        await return_to_main_menu(message)
    else:
        await message.answer("Номер не найден. Попробуйте еще раз.")
        await return_to_main_menu(message)

# Блокировка доступа
async def block_access(ip, mac):
    try:
        tn = telnetlib.Telnet(ROUTER_IP)
        tn.read_until(b"Username: ")
        tn.write(ROUTER_USERNAME.encode('ascii') + b"\n")
        tn.read_until(b"Password: ")
        tn.write(ROUTER_PASSWORD.encode('ascii') + b"\n")
        tn.write(f"block {ip} {mac}\n".encode('ascii'))  # Команда на блокировку
        tn.write(b"exit\n")
        tn.close()
    except Exception as e:
        logging.error(f"Ошибка блокировки доступа: {e}")

# Обработка выбора оплаты
@dp.message_handler(text="Оплатить", state=MenuStates.main_menu)
async def handle_payment(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = list(clients.keys())
    keyboard.add(*buttons)
    await message.answer("Выберите номер телефона для оплаты:", reply_markup=keyboard)
    await MenuStates.payment.set()

# Обработка выбора номера для оплаты
@dp.message_handler(state=MenuStates.payment)
async def process_payment(message: types.Message, state: FSMContext):
    phone = message.text
    if phone in clients:
        await message.answer("Скиньте 400 рублей на этот номер: ВТБ банк 9096598555. Жду, пока скинете чек.")
        await state.update_data(phone=phone)  # Сохраняем номер телефона
    else:
        await message.answer("Номер не найден. Попробуйте еще раз.")
        await return_to_main_menu(message)

# Обработка получения фото (чека)
@dp.message_handler(content_types=['photo'], state=MenuStates.payment)
async def check_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    if phone in clients:
        clients[phone]['paid_until'] += timedelta(days=30)  # Продление доступа на месяц
        await message.answer(f"Доступ для номера {phone} успешно продлен на месяц!")
        await message.answer("Ожидайте продления доступа... ")
        # Разблокировка доступа
        await unblock_access(clients[phone]['ip'], clients[phone]['mac'])
    else:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте ещё раз.")

    await return_to_main_menu(message)  # Возврат в главное меню

# Разблокировка доступа
async def unblock_access(ip, mac):
    try:
        tn = telnetlib.Telnet(ROUTER_IP)
        tn.read_until(b"operator: ")
        tn.write(ROUTER_USERNAME.encode('ascii') + b"\n")
        tn.read_until(b"MfUa2024: ")
        tn.write(ROUTER_PASSWORD.encode('ascii') + b"\n")
        tn.write(f"unblock {ip} {mac}\n".encode('ascii'))  # Команда на разблокировку
        tn.write(b"exit\n")
        tn.close()
    except Exception as e:
        logging.error(f"Ошибка разблокировки доступа: {e}")

# Возврат в главное меню
async def return_to_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Проверить время", "Оплатить"]
    keyboard.add(*buttons)
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)
    await MenuStates.main_menu.set()

# Запуск бота
if __name__ == '__main__':
    # Убедитесь, что `dp.loop` корректно инициализирован
    loop = asyncio.get_event_loop()
    loop.create_task(check_access_status())

    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)