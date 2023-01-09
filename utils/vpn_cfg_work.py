from loguru import logger
from os import getenv
from typing import NoReturn
import wgconfig.wgexec as wgexec
import database


class wireguard_config():
    # TODO: move it to config.py or extra module with server_cfg and client_cfg classes
    def __init__(self):
        self.cfg_path = getenv('WG_CFG_PATH')
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
            logger.error(f'[-] {e}')

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
            logger.error(f'[-] {e}')

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
                        logger.error('[-] no free ip adresses')
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
            f"[+] new peer adress is {'.'.join(adress)} for user {username}")
        return '.'.join(adress)

    def add_new_peer(self, username: str, peer_public_key: str) -> NoReturn:
        """adds new peer to config file"""
        try:
            with open(self.cfg_path, 'a') as cfg:
                cfg.write(
                    f'#{username}\n[Peer]\nPublicKey = {peer_public_key}\nAllowedIPs = {self.add_byte_to_adress(username)}/32\n\n')
                logger.info(f'[+] new peer {username} added')
        except Exception as e:
            logger.error(f'[-] {e}')

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
            logger.error(f'[-] {e}')

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
                    logger.info(
                        f"[+] peer adress for user {username} is {peer_adress[13:]}")
                    return peer_adress[13:]
        except Exception as e:
            logger.error(f'[-] {e}')

    def create_peer_config(self, peer_private_key: str, username: str) -> str:
        """creates config for client and returns it as string
        """
        return f'''[Interface]
PrivateKey = {peer_private_key}
Address = {self.last_peer_adress}
DNS = 8.8.8.8

[Peer]
PublicKey = {self.server_public_key}
PresharedKey = {self.server_preshared_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {self.server_ip}:{self.server_port}
PersistentKeepalive = 20
'''

    def update_server_config(self, username: str, device: str) -> str:
        """adds new peer to config file and restarts wg-quick

        Args:
            username (str): username of new peer
            device (str): device of new peer

        Returns:
            str: config for new peer
        """
        user_priv_key, user_pub_key = self.generate_keys()
        self.add_new_peer(f'{username}_{device}', user_pub_key)
        # restart wg-quick
        try:
            exec('sudo systemctl restart wg-quick@wg0.service')
        except Exception as e:
            logger.error(f'[-] {e}')
        else:
            logger.success('[+] wg-quick restarted successfully')

        return self.create_peer_config(user_priv_key, f'{username}_{device}')

    def disconnect_peer(self, user_id: int):
        """disconnects peer by username
        actually, it just comments all 3 lines under this username
        """
        username = database.selector.get_username_by_id(user_id)

        try:
            with open(self.cfg_path, 'r') as cfg:
                config = cfg.read()
                for line in config.splitlines():
                    if line.startswith(f'#{username}'):
                        config = config.replace(
                            f'{line}\n', f'#DISCONNECTED_{line[1:]}\n')

            with open(self.cfg_path, 'w') as cfg:
                cfg.write(config)

            # comment 3 lines under username such as: Peer, PublicKey, AllowedIPs
            with open(self.cfg_path, 'r') as cfg:
                config = cfg.read()
                config_as_list = config.splitlines()
                for line in config_as_list:
                    if line.startswith(f'#DISCONNECTED_{username}'):
                        # get index of line with username
                        line_index = config.splitlines().index(line)
                        # check if next line is #[Peer] then not comment it and next 2 lines twice or more
                        if not config_as_list[line_index + 1].startswith('#[Peer]'):
                            for _ in range(3):
                                line_index += 1
                                config_as_list[line_index] = f'#{config_as_list[line_index]}'

                config = ''.join([f'{line}\n' for line in config_as_list])

            with open(self.cfg_path, 'w') as cfg:
                cfg.write(config)
                # restart wg-quick
                exec('sudo systemctl restart wg-quick@wg0.service')
                logger.info(f'[+] peer {username} disconnected')

        except Exception as e:
            logger.error(f'[-] {e}')

    def reconnect_payed_user(self, user_id: int):
        """reconnects payed user by user_id
        """
        username = database.selector.get_username_by_id(user_id)

        try:
            with open(self.cfg_path, 'r') as cfg:
                config = cfg.read()
                for line in config.splitlines():
                    if line.startswith(f'#DISCONNECTED_{username}'):
                        config = config.replace(
                            f'{line}\n', f'#{line[14:]}\n')

            with open(self.cfg_path, 'w') as cfg:
                cfg.write(config)

            with open(self.cfg_path, 'r') as cfg:
                config = cfg.read()
                config_as_list = config.splitlines()
                for line in config_as_list:
                    if line.startswith(f'#{username}'):
                        # get index of line with username
                        line_index = config.splitlines().index(line)
                        if config_as_list[line_index + 1].startswith('#[Peer]'):
                            for _ in range(3):
                                line_index += 1
                                config_as_list[line_index] = config_as_list[line_index][1:]

                config = ''.join([f'{line}\n' for line in config_as_list])

            with open(self.cfg_path, 'w') as cfg:
                cfg.write(config)
                # restart wg-quick
                exec('sudo systemctl restart wg-quick@wg0.service')
                logger.info(f'[+] peer {username} reconnected')

        except Exception as e:
            logger.error(f'[-] {e}')
