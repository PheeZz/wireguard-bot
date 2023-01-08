import psycopg2 as pg
from loguru import logger
from data.config import db_connection_parameters as params
from datetime import datetime, timedelta


def update_user_payment(user_id: int) -> None:
    """ Update user payment end date in table users
    add 30 days to current date"""
    try:
        conn = pg.connect(**params)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = %s WHERE user_id = %s
                """, (datetime.now() + timedelta(days=30), user_id))

            conn.commit()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f'[-] {error}')
        return None
