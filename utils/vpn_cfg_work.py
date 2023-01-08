from loguru import logger
from os import getenv
from typing import NoReturn
import wgconfig.wgexec as wgexec


class wireguard_config():
    # TODO: move it to config.py or extra module with server_cfg and client_cfg classes
    def __init__(self):
        # self.cfg_path = getenv('WG_CFG_PATH')
        self.cfg_path = './utils/config_test.conf'
        self.server_ip = getenv('WG_SERVER_IP')
        self.server_port = getenv('WG_SERVER_PORT')
        self.server_public_key = getenv('WG_SERVER_PUBLIC_KEY')
        self.server_preshared_key = getenv('WG_SERVER_PRESHARED_KEY')

        self.config = self.get_config()
        self.last_peer_adress = self.get_last_peer_adress()

    def get_config(self) -> str:
        try:
            with open(self.cfg_path, 'r') as cfg:
                return cfg.read()
        except Exception as e:
            logger.error(f'[✗] {e}')

    def get_last_peer_adress(self) -> str:
        """returns last peer adress from config file
        exactly, the last string in config file, that starts with 'AllowedIPs'"""
        try:
            for line in self.config.splitlines():
                if line.startswith('AllowedIPs'):
                    last_peer_adress = line
            # delete 'AllowedIPs = ' and '/32' from string
            return last_peer_adress[13:-3]
        except Exception as e:
            logger.error(f'[✗] {e}')

    def add_byte_to_adress(self, username: str) -> str:
        """adds 1 byte to adress
        """
        adress = self.last_peer_adress.split('.')
        if adress[-1] == '255':
            adress[-1] = '1'
            if adress[-2] == '255':
                adress[-2] = '0'
                if adress[-3] == '255':
                    adress[-3] = '0'
                    if adress[-4] == '255':
                        logger.error('[✗] no free ip adresses')
                        return
                    else:
                        adress[-4] = str(int(adress[-4]) + 1)
                else:
                    adress[-3] = str(int(adress[-3]) + 1)
            else:
                adress[-2] = str(int(adress[-2]) + 1)
        else:
            adress[-1] = str(int(adress[-1]) + 1)

        logger.info(
            f"[✓] new peer adress is {'.'.join(adress)} for user {username}")
        return '.'.join(adress)

    def add_new_peer(self, username: str, peer_public_key: str) -> NoReturn:
        """adds new peer to config file"""
        try:
            with open(self.cfg_path, 'a') as cfg:
                cfg.write(
                    f'# {username}\n[Peer]\nPublicKey = {peer_public_key}\nAllowedIPs = {self.add_byte_to_adress(username)}/32\n\n')

        except Exception as e:
            logger.error(f'[✗] {e}')

        else:
            # update config and last_peer_adress variables after adding new peer
            self.config = self.get_config()
            self.last_peer_adress = self.get_last_peer_adress()

    def generate_keys(self) -> tuple[str, str]:
        """generates private and public keys
        """
        try:
            private_key, public_key = wgexec.generate_keypair()
            return private_key, public_key
        except Exception as e:
            logger.error(f'[✗] {e}')

    def get_peer_adress(self, username: str) -> str:
        """returns peer adress by username
        """
        try:
            for line in self.config.splitlines():
                if line.startswith('#') and line[2:] == username:
                    for line in self.config.splitlines():
                        if line.startswith('AllowedIPs'):
                            peer_adress = line
                    # delete 'AllowedIPs = ' from string
                    return peer_adress[13:]
        except Exception as e:
            logger.error(f'[✗] {e}')

    def create_peer_config(self, peer_private_key: str, username: str) -> str:
        """creates config for client and returns it as string
        """
        return f'''[Interface]
PrivateKey = {peer_private_key}
Address = {self.get_peer_adress(username)}
DNS = 8.8.8.8

[Peer]
PublicKey = {self.server_public_key}
PresharedKey = {self.server_preshared_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {self.server_ip}:{self.server_port}
PersistentKeepalive = 20
'''

    def update_server_config(self, username: str, device: str) -> str:
        user_pub_key, user_priv_key = self.generate_keys()
        self.add_new_peer(f'{username}_{device}', user_pub_key)
        return self.create_peer_config(user_priv_key, f'{username}_{device}')


if __name__ == '__main__':
    server_config = wireguard_config()
    # print(server_config.last_peer_adress)
    # server_config.add_new_peer(username='QA_engeneer', peer_public_key='test')
    # print(server_config.last_peer_adress)
    # print(server_config.get_peer_adress(username='QA_engeneer'))
    print(server_config.create_peer_config(
        peer_private_key='test', username='QA_engeneer'))
