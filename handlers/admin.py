from ast import parse
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified


from data import config
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
