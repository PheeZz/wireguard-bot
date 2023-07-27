from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import bot, vpn_config

from data import config
import database
import keyboards as kb
from middlewares import rate_limit

from pprint import pformat
from datetime import datetime


def is_admin(func):
    async def wrapped(message: types.Message, state: FSMContext):
        if message.from_user.id in config.ADMINS:
            await func(message, state)
        else:
            await message.answer(
                "You don't have permission to use this command.\n\Write to @pheezz for more info."
            )

    return wrapped


@rate_limit(limit=3)
@is_admin
# function for getting info about message in pretty format
async def cmd_info(message: types.Message, state: FSMContext) -> types.Message | str:
    await message.answer(
        f"<pre>{pformat(message.to_python())}</pre>", parse_mode="HTML"
    )


@rate_limit(limit=3)
@is_admin
async def statistic_endtime(message: types.Message, state: FSMContext):
    args = message.text.split()[1:]
    users = database.selector.get_all_usernames_and_enddate()
    # sort by enddate high to low
    users.sort(key=lambda x: x[1], reverse=True)

    if "active" in args:
        users = [user for user in users if user[1] >= datetime.now()]

    elif ("inactive" in args) or ("notactive" in args) or ("expired" in args):
        users = [user for user in users if user[1] < datetime.now()]

    pretty_string = "".join(
        [f'{user[0]} - {user[1].strftime("%d-%m-%Y")}\n' for user in users]
    )
    await message.answer(f"<pre>{pretty_string}</pre>", parse_mode="HTML")


@rate_limit(limit=3)
@is_admin
async def give_subscription_time(
    message: types.Message, state: FSMContext
) -> types.Message:
    # /give pheezz 30
    # or /give 123456789 30

    if message.text.split()[1].isdigit():
        user_id = int(message.text.split()[1])
        days = message.text.split()[2]
    else:
        username, days = message.text.split()[1:]
        user_id = database.selector.get_user_id(username)

    try:
        database.update.update_given_subscription_time(user_id=user_id, days=int(days))
        if database.selector.is_subscription_expired(user_id):
            vpn_config.disconnect_peer(user_id)
            await bot.send_message(
                user_id,
                "Ваша подписка истекла.",
                reply_markup=await kb.free_user_kb(),
            )
    except Exception as e:
        await message.answer(f"Error: {e}")
    else:
        vpn_config.reconnect_payed_user(user_id=user_id)
        await bot.send_message(
            user_id,
            f"Поздравляем! Администратор продлил вашу подписку на {days} дней!",
            reply_markup=await kb.payed_user_kb(),
        )
        await message.answer(
            f"""Пользователю {user_id} продлена подписка на {days} дней
теперь она актуальна до: {database.selector.get_subscription_end_date(user_id)}"""
        )


@rate_limit(limit=3)
@is_admin
async def restart_wg_service_admin(message: types.Message, state: FSMContext):
    vpn_config.restart_wg_service()
    await message.answer("Сервис WireGuard перезапущен")
