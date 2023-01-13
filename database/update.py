import psycopg2 as pg
from loguru import logger
from data.config import db_connection_parameters as params
from datetime import datetime, timedelta
from typing import NoReturn


def update_user_payment(user_id: int) -> NoReturn:
    """ Update user payment end date in table users
    add 30 days to current date if user don't have subscription at the moment
    and add 30 days to date in subscription_end_date if user have not expired subscription now
    """
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = CASE
                WHEN subscription_end_date < %s THEN %s + %s
                ELSE subscription_end_date + %s END
                WHERE user_id = %s
                """, (datetime.now(), datetime.now(),
                      timedelta(days=30), timedelta(days=30), user_id))

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """, (user_id,))
            username = cursor.fetchone()[0]

            logger.info(
                f'[+] user {user_id}::{username} payment updated; added: 30 days')
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return None


def update_user_config_count(user_id: int) -> NoReturn:
    """ Update user config count in table users
    add 1 to current config count"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET config_count = config_count + 1 WHERE user_id = %s
                """, (user_id,))

            conn.commit()
            logger.info(
                f'[+] user {user_id} config count updated to {cursor.rowcount}')
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return None


def update_given_subscription_time(user_id: int, days: int) -> NoReturn:
    """ Update user payment end date in table users
    add given days to date in table"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users
                SET subscription_end_date = subscription_end_date + %s
                WHERE user_id = %s
                """, (timedelta(days=days), user_id))

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """, (user_id,))
            username = cursor.fetchone()[0]

            logger.info(
                f'[+] user {user_id}::{username} payment updated [BY ADMIN]; added: {days} days')
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return None


def set_user_enddate_to_N(user_id: int, days: int) -> NoReturn:
    """ Update user payment end date in table users
    set date to datetime.now() + N days"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = %s WHERE user_id = %s
                """, (datetime.now() + timedelta(days=days), user_id))

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """, (user_id,))
            username = cursor.fetchone()[0]

            logger.info(
                f'''[+] user {user_id}::{username} payment updated [BY ADMIN]; set to:
                {datetime.now() + timedelta(days=days)}''')
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return None
