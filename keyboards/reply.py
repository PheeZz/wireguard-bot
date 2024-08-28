from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from database.selector import all_user_configs, is_user_have_config


async def payed_user_kb():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    keyboard.insert(KeyboardButton("🕑 Моя подписка"))
    keyboard.insert(KeyboardButton("📝 Помощь"))
    keyboard.insert(KeyboardButton("☢️Перезагрузить VPN"))
    return keyboard


async def free_user_kb(user_id: int):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(
        KeyboardButton(
            "💵 Оплатить",
        )
    )
    if is_user_have_config(user_id=user_id):
        keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    return keyboard


async def configs_kb(user_id: int):
    configs_kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    configs = all_user_configs(user_id=user_id)

    if configs:
        for config in configs:
            configs_kb.insert(
                KeyboardButton(f"🔐 {'ПК' if config[0].split('_')[-1] == 'PC' else 'Смартфон'}")
            )

    if not configs or len(configs) < 2:
        configs_kb.insert(KeyboardButton("🆕 Создать конфиг"))

    configs_kb.insert(KeyboardButton("🔙 Назад"))

    return configs_kb


async def subscription_management_kb():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📅 Дата отключения"))
    keyboard.insert(KeyboardButton("💵 Продлить"))
    keyboard.insert(KeyboardButton("🔙 Назад"))
    return keyboard
