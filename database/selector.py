import psycopg2 as pg
from loguru import logger
from data.config import db_connection_parameters as params
from datetime import datetime


def is_exist_user(user_id: int) -> bool:
    """ Check if user is exist in database"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)
                """, (user_id,)
            )
            return cursor.fetchone()[0]

    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False


def is_user_have_config(user_id: int) -> bool:
    """ Check if user have config in database"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT EXISTS(SELECT 1 FROM vpn_config WHERE user_id = %s)
                """, (user_id,)
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False


def all_user_configs(user_id: int) -> list:
    """ Get all user configs"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT config_name FROM vpn_config WHERE user_id = %s
                """, (user_id,)
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False


def is_subscription_end(user_id: int) -> bool:
    """ Check if user subscription is end"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT subscription_end_date FROM users WHERE user_id = %s
                """, (user_id,)
            )
            date = cursor.fetchone()[0]
            return date < datetime.now()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False


def get_subscription_end_date(user_id: int) -> datetime:
    """ Get user subscription end date"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT subscription_end_date FROM users WHERE user_id = %s
                """, (user_id,)
            )
            # return date in format: day-month-year
            return cursor.fetchone()[0].strftime('%d-%m-%Y')
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False


def get_user_config(user_id: int, config_name: str) -> str:
    """ Get user config"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT config FROM vpn_config WHERE user_id = %s AND config_name = %s
                """, (user_id, config_name)
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return False