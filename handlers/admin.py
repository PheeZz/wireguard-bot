from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import bot, vpn_config

from data import config
import database
import keyboards as kb
from middlewares import rate_limit

from pprint import pformat
from datetime import datetime
from aiogram.utils.markdown import hcode, hbold, hpre
from io import BytesIO


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
        f"{hpre(pformat(message.to_python()))}", parse_mode=types.ParseMode.HTML
    )


@rate_limit(limit=3)
@is_admin
async def statistic_endtime(message: types.Message, state: FSMContext):
    args = message.text.split()[1:]
    users = database.selector.get_all_usernames_and_enddate()
    if not users:
        await message.answer(
            f"{hbold('No users found')}", parse_mode=types.ParseMode.HTML
        )
        return
    # sort by enddate high to low
    users.sort(key=lambda x: x[1], reverse=True)

    if "active" in args:
        users = [user for user in users if user[1] >= datetime.now()]

    elif ("inactive" in args) or ("notactive" in args) or ("expired" in args):
        users = [user for user in users if user[1] < datetime.now()]

    pretty_string = "".join(
        [f'{user[0]} - {user[1].strftime("%d-%m-%Y")}\n' for user in users]
    )

    if len(pretty_string) > 4096:
        io_string = BytesIO(pretty_string.encode("utf-8"))
        await message.answer_document(
            types.InputFile(
                io_string,
                filename=f"statistic_endtime_{datetime.now().strftime('%d-%m-%Y')}.txt",
            )
        )
    else:
        await message.answer(
            f"{hcode('username')} - {hbold('enddate')}\n\n{pretty_string}",
            parse_mode=types.ParseMode.HTML,
        )


@rate_limit(limit=3)
@is_admin
async def give_subscription_time(
    message: types.Message, state: FSMContext
) -> types.Message:
    # /give pheezz 30
    # or /give 123456789 30
    if len(message.text.split()) != 3:
        message.answer(
            f"Неверный формат команды\n"
            f"{hcode('/give username days')}\n"
            f"{hcode('/give user_id days')}"
        )
        return

    if message.text.split()[1].isdigit():
        user_id = int(message.text.split()[1])
        days = message.text.split()[2]
    else:
        username, days = message.text.split()[1:]
        user_id = database.selector.get_user_id(username)

    try:
        database.update.update_given_subscription_time(user_id=user_id, days=int(days))
        is_subscription_expired = database.selector.is_subscription_expired(user_id)
        if is_subscription_expired:
            vpn_config.disconnect_peer(user_id)
            await bot.send_message(
                user_id,
                "Ваша подписка истекла.",
                reply_markup=await kb.free_user_kb(user_id=user_id),
            )
    except Exception as e:
        await message.answer(f"Error: {e.__repr__()}")
    else:
        if not is_subscription_expired:
            vpn_config.reconnect_payed_user(user_id=user_id)
        await bot.send_message(
            user_id,
            f"Поздравляем! Администратор продлил вашу подписку на {hbold(days)} дней!",
            reply_markup=await kb.payed_user_kb()
            if not is_subscription_expired
            else await kb.free_user_kb(user_id=user_id),
            parse_mode=types.ParseMode.HTML,
        )
        for admin in config.ADMINS:
            await bot.send_message(
                chat_id=admin,
                text=f"Пользователю {hcode(user_id)} продлена подписка на {hbold(days)} дней.\n"
                f"Теперь она актуальна до: {hbold(database.selector.get_subscription_end_date(user_id))}",
                parse_mode=types.ParseMode.HTML,
            )


@rate_limit(limit=3)
@is_admin
async def restart_wg_service_admin(message: types.Message, state: FSMContext):
    vpn_config.restart_service()
    await message.answer("Сервис WireGuard перезапущен")
