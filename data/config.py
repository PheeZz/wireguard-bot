import os
from dotenv import load_dotenv
from utils.vpn_cfg_work import wireguard_config

load_dotenv(override=True)

BOT_TOKEN = os.getenv('WG_BOT_TOKEN')
PAYMENTS_TOKEN = os.getenv('PAYMENTS_TOKEN')
ADMINS = os.getenv('ADMINS_IDS')

db_connection_parameters = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_USER_PASSWORD'),
    'database': os.getenv('DATABASE'),
}

vpn_config = wireguard_config()

if __name__ == '__main__':
    print(BOT_TOKEN)
    print(PAYMENTS_TOKEN)
    print(ADMINS)
