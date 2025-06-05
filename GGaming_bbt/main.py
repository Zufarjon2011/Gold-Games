from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from register_players import register_handlers, RegisterState, LoginState
from keyboards import main_menu_keyboard, logout_keyboard
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '7919206466:AAGFvjaG8pfyq9aFMgHlVQsU3pbMEuR3LAk'

bot = Bot(token=API_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers(dp, bot)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=main_menu_keyboard())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
