from aiogram import executor


async def set_commands(dp):
    from aiogram import types

    await dp.bot.set_my_commands(
        commands=[
            types.BotCommand(
                command='/start',
                description='start bot'),
        ])


async def on_startup(dp):
    import handlers
    import middlewares
    from loguru import logger
    import time
    from utils.Watchdog import Watchdog

    middlewares.setup(dp)
    await set_commands(dp)
    handlers.setup(dp)

    logger.add(f'logs/{time.strftime("%Y-%m-%d__%H-%M")}.log',
               level='DEBUG', rotation='500 MB', compression='zip')

    daemon = Watchdog()
    daemon.run()
    logger.success('[+] Bot started successfully')

if __name__ == "__main__":
    # Launch
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
