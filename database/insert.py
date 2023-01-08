import psycopg2 as pg
from typing import NoReturn
from loguru import logger
from data.config import db_connection_parameters as params
from aiogram.types import Message
from datetime import datetime

from pprint import pprint


def insert_new_user(message: Message) -> NoReturn:
    """ Insert new user in table users if he is not in database"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                INSERT INTO users(user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING
                """, (message.from_user.id, message.from_user.username)
            )
            conn.commit()
            logger.success(
                f"[✓] User {message.from_user.username} added to database")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')


def insert_new_payment(message: Message) -> NoReturn:
    """ Insert new payment in table payment"""
    pprint(message)
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                INSERT INTO payment(user_id, date, amount)
                VALUES (%s, %s)
                """, (message.from_user.id, datetime.now(), message.successful_payment.total_amount)
            )
            conn.commit()
            logger.success(
                f"[✓] Payment {message.successful_payment.invoice_payload} added to database")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')


def insert_new_config(user_id: int, username: str, device: str, config: str) -> NoReturn:
    """ Insert new config in table vpn_config"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                INSERT INTO vpn_config(user_id, config_name, config)
                VALUES (%s, %s, %s)
                """, (user_id, f'{username}_{device}', config)
            )
            conn.commit()
            logger.success(
                f"[✓] Config {username}_{device} added to database")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')
