from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import random, string, importlib.util, os, re
from keyboards import main_menu_keyboard, logout_keyboard, admin_keyboard

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_password = State()

class LoginState(StatesGroup):
    waiting_for_class = State()
    waiting_for_password = State()

class EditState(StatesGroup):
    waiting_for_password = State()
    waiting_for_new_code = State()

def register_handlers(dp: Dispatcher, bot):

    def get_user_by_class(class_name):
        spec = importlib.util.spec_from_file_location("users_db", "users_db.py")
        users_db = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(users_db)
        return getattr(users_db, class_name, None)

    def get_user_by_password(password):
        with open("users_db.py", "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(r'class (\w+):\n(.*?)Password = ["\'](.+?)["\']', content, re.DOTALL)
            for classname, _, pwd in matches:
                if pwd == password:
                    return classname
        return None

    def save_user_to_file(class_name, fullname, password):
        with open("users_db.py", "a", encoding="utf-8") as f:
            f.write(f"\n\nclass {class_name}:\n")
            f.write(f"    Password = \"{password}\"\n")
            f.write(f"    userfullname = \"{fullname}\"\n")
            f.write(f"    status = \"player\"\n")
            f.write(f"    games = \"none\"\n")
            f.write(f"    experience = \"beginner\"\n")

    def generate_random_classname():
        digits = ''.join(random.choices(string.digits, k=random.randint(4,7)))
        letters = ''.join(random.choices(string.ascii_lowercase, k=4))
        return f"user{digits}{letters}"

    # ---------------- Регистрация ----------------
    @dp.message_handler(lambda m: m.text == "📝 Регистрация")
    async def start_registration(message: types.Message, state: FSMContext):
        await message.delete()
        await message.answer("Введите ваше полное имя:", reply_markup=types.ReplyKeyboardRemove())
        await RegisterState.waiting_for_name.set()

    @dp.message_handler(state=RegisterState.waiting_for_name)
    async def process_name(message: types.Message, state: FSMContext):
        await message.delete()
        await state.update_data(fullname=message.text.strip())
        await message.answer("Создайте пароль:")
        await RegisterState.waiting_for_password.set()

    @dp.message_handler(state=RegisterState.waiting_for_password)
    async def process_password(message: types.Message, state: FSMContext):
        await message.delete()
        data = await state.get_data()
        fullname = data['fullname']
        password = message.text.strip()
        class_name = generate_random_classname()
        save_user_to_file(class_name, fullname, password)

        channel_id = message.chat.id
        await bot.send_message(
            chat_id=channel_id,
            text=f"-----------New User-------------\n"
                 f"nick name: {message.from_user.first_name}\n"
                 f"user name: @{message.from_user.username}\n"
                 f"user id: {message.from_user.id}\n"
                 f"---------------------------------------\n"
        )

        await message.answer(f"✅ Регистрация завершена!\nВаш ID: <code>{class_name}</code>",
                             reply_markup=logout_keyboard())
        await state.finish()

    # ---------------- Логин ----------------
    @dp.message_handler(lambda m: m.text == "🔑 Логин")
    async def start_login(message: types.Message, state: FSMContext):
        await message.delete()
        await message.answer("Введите ваш ID:", reply_markup=types.ReplyKeyboardRemove())
        await LoginState.waiting_for_class.set()

    @dp.message_handler(state=LoginState.waiting_for_class)
    async def login_class(message: types.Message, state: FSMContext):
        await state.update_data(class_name=message.text.strip())
        await message.answer("Введите пароль:")
        await LoginState.waiting_for_password.set()

    @dp.message_handler(state=LoginState.waiting_for_password)
    async def login_user(message: types.Message, state: FSMContext):
        await message.delete()
        data = await state.get_data()
        class_name = data['class_name']
        password = message.text.strip()
        user = get_user_by_class(class_name)

        if user and getattr(user, 'Password', None) == password:
            if getattr(user, 'status', '') == 'Admin':
                await message.answer(f"👑 Добро пожаловать, Админ {user.userfullname}!", reply_markup=admin_keyboard())
            else:
                await message.answer(f"✅ Добро пожаловать, {user.userfullname}!", reply_markup=logout_keyboard())
        else:
            await message.answer("❌ Неверный ID или пароль", reply_markup=main_menu_keyboard())

        await state.finish()

    # ---------------- Logout ----------------
    @dp.message_handler(lambda m: m.text == "🚪 Выйти")
    async def logout(message: types.Message, state: FSMContext):
        await message.delete()
        await message.answer("Вы вышли из аккаунта.", reply_markup=main_menu_keyboard())
        await state.finish()

    # ---------------- Admin: Редактирование ----------------
    @dp.message_handler(lambda m: m.text == "✏️ Редактировать пользователя")
    async def ask_edit_password(message: types.Message):
        await message.answer("Введите пароль пользователя, которого хотите отредактировать:")
        await EditState.waiting_for_password.set()

    @dp.message_handler(state=EditState.waiting_for_password)
    async def find_user_to_edit(message: types.Message, state: FSMContext):
        await message.delete()
        password = message.text.strip()
        class_name = get_user_by_password(password)

        if class_name:
            with open("users_db.py", "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(rf'class {class_name}:(.*?)(?=\nclass |\Z)', content, re.DOTALL)
                if match:
                    await state.update_data(class_name=class_name)
                    await message.answer(f"Отредактируйте пользователя и отправьте:\n\n<code>class {class_name}:{match.group(1)}</code>",
                                         parse_mode="HTML")
                    await EditState.waiting_for_new_code.set()
        else:
            await message.answer("❌ Пользователь с таким паролем не найден.")
            await state.finish()

    @dp.message_handler(state=EditState.waiting_for_new_code, content_types=types.ContentTypes.TEXT)
    async def save_new_user_class(message: types.Message, state: FSMContext):
        new_code = message.text.strip()
        data = await state.get_data()
        class_name = data['class_name']

        with open("users_db.py", "r+", encoding="utf-8") as f:
            content = f.read()
            updated_content = re.sub(rf'class {class_name}:(.*?)(?=\nclass |\Z)',
                                     new_code,
                                     content, flags=re.DOTALL)
            f.seek(0)
            f.write(updated_content)
            f.truncate()

        await message.answer("✅ Пользователь успешно обновлён!", reply_markup=admin_keyboard())
        await state.finish()
