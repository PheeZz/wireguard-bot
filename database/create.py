import psycopg2 as pg
from typing import NoReturn
from loguru import logger
from data.config import db_connection_parameters as params


# params = {
#     'database': 'wireguard_bot',
#     'user': 'postgres',
#     'password': 'postgres',
#     'host': 'localhost',
#     'port': '5432',
# }


def create_table_user() -> NoReturn:
    """ Create table user in database wireguard_bot"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id INT UNIQUE,
                username VARCHAR(255) UNIQUE,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                subscription_end_date TIMESTAMP,
                config_count INT DEFAULT 0)
                """
            )
            conn.commit()
            logger.success("[✓] Table user created successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')


def create_table_payment() -> NoReturn:
    """ Create table payment in database wireguard_bot"""
    try:
        conn = pg.connect(**params)

        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                CREATE TABLE IF NOT EXISTS payment(
                id SERIAL PRIMARY KEY,
                user_id INT,
                amount INT,
                date TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
            )
            conn.commit()
            logger.success("[✓] Table payment created successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')


def create_table_vpn_config() -> NoReturn:
    """ Create table vpn_config in database wireguard_bot"""
    try:
        conn = pg.connect(**params)

        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                CREATE TABLE IF NOT EXISTS vpn_config (
                id SERIAL PRIMARY KEY,
                user_id INT,
                config_name VARCHAR(255),
                config TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id))
                """
            )
            conn.commit()
            logger.success("[✓] Table vpn_config created successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[✗] {error}')


if __name__ == "__main__":
    create_table_user()
    create_table_payment()
    create_table_vpn_config()
