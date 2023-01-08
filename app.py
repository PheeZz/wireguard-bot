from aiogram import executor


async def set_commands(dp):
    from aiogram import types

    await dp.bot.set_my_commands(
        commands=[
            types.BotCommand(
                command='/menu',
                description='menu'),
        ])


async def on_startup(dp):
    import handlers
    import middlewares
    from loguru import logger
    import time

    middlewares.setup(dp)
    await set_commands(dp)
    handlers.setup(dp)

    logger.add(f'logs/{time.strftime("%Y-%m-%d__%H-%M")}.log',
               level='DEBUG', rotation='500 MB', compression='zip')

if __name__ == "__main__":
    # Launch
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
