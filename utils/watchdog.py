# ASYNC daemon that watches for users who have a subscription end date and sends them a message
# first time : 2 days before end date
# second time : 1 day before end date
# third time : end date
# fourth time : 1 day after end date send kb free user

from loguru import logger
from database.selector import get_user_ids_enddate_n_days
import keyboards as kb
from loader import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import vpn_config


class Watchdog:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """start watchdog coroutine every day at 02:00"""
        self.scheduler.add_job(self.check_end_date, "cron", hour=2, minute=0)
        # self.scheduler.add_job(self.check_end_date, 'interval', seconds=5)
        self.scheduler.start()
        logger.success("[+] Watchdog coroutine created and started successfully")

    async def check_end_date(self):
        logger.info("[+] Checking for users with end date")
        notified_users = []
        user_ids_by_day = {}
        for days in range(-1, 3):
            user_ids_by_day[days] = get_user_ids_enddate_n_days(days)
            for user_id in user_ids_by_day[days]:
                if user_id not in notified_users:
                    message_text = self.get_message_text(days)
                    if days == -1:
                        await bot.send_message(
                            user_id,
                            message_text,
                            reply_markup=await kb.reply.free_user_kb(user_id=user_id),
                        )
                        vpn_config.disconnect_peer(user_id)
                    else:
                        await bot.send_message(user_id, message_text)
                    notified_users.append(user_id)
                    logger.warning(
                        f"[+] user {user_id} notified about end date {days} days"
                    )

        logger.info("Finished checking for users with end date")

    def get_message_text(self, days: int) -> str:
        if days == -1:
            return "Ваша подписка закончилась, но вы можете продлить ее =)"
        elif days == 0:
            return "Сегодня заканчивается ваша подписка, не забудьте продлить ее =)"
        elif days == 1:
            return "Ваша подписка заканчивается завтра, не забудьте продлить ее =)"
        elif days == 2:
            return "Ваша подписка заканчивается через 2 дня, не забудьте продлить ее =)"

    def stop(self):
        self.scheduler.shutdown()
