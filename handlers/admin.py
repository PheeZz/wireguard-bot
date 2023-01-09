from ast import parse
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified
from loader import bot

from data import config
import database
import keyboards as kb
from middlewares import rate_limit

from pprint import pformat


def is_admin(func):
    async def wrapped(message: types.Message, state: FSMContext):
        if message.from_user.id in config.ADMINS:
            await func(message, state)
        else:
            await message.answer("You don't have permission to use this bot.\n\Write to @pheezz for more info.")
    return wrapped


@rate_limit(limit=3)
@is_admin
# function for getting info about message in pretty format
async def cmd_info(message: types.Message, state: FSMContext) -> types.Message | str:
    await message.answer(f'<pre>{pformat(message.to_python())}</pre>',
                         parse_mode='HTML')


@rate_limit(limit=3)
@is_admin
async def statistic_endtime(message: types.Message, state: FSMContext):
    users = database.selector.get_all_usernames_and_enddate()
    pretty_string = ''.join(
        [f'{user[0]} - {user[1].strftime("%d-%m-%Y")}\n' for user in users])
    await message.answer(f'<pre>{pretty_string}</pre>', parse_mode='HTML')


@rate_limit(limit=3)
@is_admin
async def give_subscription_time(message: types.Message, state: FSMContext) -> types.Message:
    # /give pheezz 30
    username, days = message.text.split()[1:]
    user_id = database.selector.get_user_id(username)
    try:
        database.update.update_given_subscription_time(
            user_id=user_id, days=int(days))
    except Exception as e:
        await message.answer(f'Error: {e}')
    else:
        await bot.send_message(
            user_id, f'Поздравляем! Администратор продлил вашу подписку на {days} дней!', reply_markup=await kb.payed_user_kb())
        await message.answer(f'Пользователю {username} продлена подписка на {days} дней\nтеперь она актуальна до: {database.selector.get_subscription_end_date(user_id)}')
