from aiogram import types

def main_menu_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📝 Регистрация", "🔑 Логин")
    return kb

def logout_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚪 Выйти")
    return kb

def admin_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✏️ Редактировать пользователя", "🚪 Выйти")
    return kb
