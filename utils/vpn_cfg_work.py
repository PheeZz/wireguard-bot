from loguru import logger
from os import getenv
import database
import subprocess
from ipaddress import IPv4Address


class WireguardConfig:
    # TODO: move it to config.py or extra module with server_cfg and client_cfg classes
    def __init__(self):
        self.cfg_path = getenv("WG_CFG_PATH")
        self.server_ip = getenv("WG_SERVER_IP")
        self.server_port = getenv("WG_SERVER_PORT")
        self.server_public_key = getenv("WG_SERVER_PUBLIC_KEY")
        self.server_preshared_key = getenv("WG_SERVER_PRESHARED_KEY")

        self.config = self.get_config()
        self.last_peer_adress = self.get_last_peer_adress()

    def generate_private_key(self, username: str, save: bool = True) -> str:
        """Generate wireguard peer PRIVATE key

        Returns:
            str: peer private key
        """
        try:
            private_key = (
                subprocess.check_output("wg genkey", shell=True).decode("utf-8").strip()
            )
            logger.success("[+] private key generated")

            if save:
                # TODO maybe better save private key to database?
                logger.info(
                    f'[+] private key "{private_key}" for user {username} saved to database'
                )

            return private_key
        except Exception as e:
            logger.error(f"[-] {e}")

    def generate_public_key(
        self, private_key: str, username: str, save: bool = True
    ) -> str:
        """Generate wireguard peer PUBLIC key

        Args:
            private_key (str): peer private key,
            can be generated with self.generate_private_key()

        Returns:
            str: peer PUBLIC key
        """
        try:
            public_key = (
                subprocess.check_output(f"echo '{private_key}' | wg pubkey", shell=True)
                .decode("utf-8")
                .strip()
            )
            logger.success("[+] public key generated")

            if save:
                # TODO maybe better save public key to database?
                logger.info(
                    f'[+] public key "{public_key}" for user {username} saved to database'
                )

            return public_key
        except Exception as e:
            logger.error(f"[-] {e}")

    def generate_key_pair(self, username: str) -> tuple:
        private_key = self.generate_private_key(username=username)
        public_key = self.generate_public_key(private_key, username=username)
        return private_key, public_key

    def restart_service(self) -> None:
        """restart wireguard service"""
        try:
            subprocess.run(["sudo", "systemctl", "restart", "wg-quick@wg0.service"])
            logger.success("[+] wireguard service restarted")
        except Exception as e:
            logger.error(f"[-] {e}")

    def get_config(self) -> str:
        try:
            with open(self.cfg_path, "r") as cfg:
                return cfg.read()
        except Exception as e:
            logger.error(f"[-] {e}")

    def get_last_peer_adress(self) -> str:
        """returns last peer adress from config file
        exactly, the last string in config file, that starts with 'AllowedIPs'"""
        try:
            for line in self.config.splitlines():
                if line.startswith("AllowedIPs"):
                    last_peer_adress = line
            # delete 'AllowedIPs = ' and '/32' from string
            return last_peer_adress[13:-3]
        except Exception as e:
            logger.error(f"[-] {e.__repr__()}")

    def add_byte_to_adress(self, username: str) -> str | None:
        """adds 1 byte to adress"""
        adress = IPv4Address(self.last_peer_adress)
        if adress == IPv4Address("255.255.255.255"):
            logger.error("[-] no free ip adresses")
            return None

        new_adress = str(adress + 1)
        logger.info(f"[+] new peer adress is {new_adress} for user {username}")

        return new_adress

    def add_new_peer(self, username_and_device: str, peer_public_key: str) -> None:
        """adds new peer to config file"""
        try:
            with open(self.cfg_path, "a") as cfg:
                cfg.write(
                    f"#{username_and_device}\n"
                    f"[Peer]\n"
                    f"PublicKey = {peer_public_key}\n"
                    f"PresharedKey = {self.server_preshared_key}\n"
                    f"AllowedIPs = {self.add_byte_to_adress(username_and_device)}/32\n\n"
                )
                logger.info(f"[+] new peer {username_and_device} added")
        except Exception as e:
            logger.error(f"[-] {e}")

        else:
            # update config and last_peer_adress variables after adding new peer
            self.config = self.get_config()
            self.last_peer_adress = self.get_last_peer_adress()

    def get_peer_address(self, username: str) -> str:
        """Returns peer address by username"""
        for line in self.config.splitlines():
            if line.startswith("#") and line[2:] == username:
                for line2 in self.config.splitlines():
                    if line2.startswith("AllowedIPs") or line2.startswith(
                        "#AllowedIPs"
                    ):
                        peer_address = line2
                # Remove 'AllowedIPs = ' from the string
                logger.info(
                    f"[+] Peer address for user {username} is {peer_address[13:]}"
                )
                return (
                    peer_address[13:]
                    if line2.startswith("AllowedIPs")
                    else peer_address[14:]
                )
        logger.error("[-] Peer address not found")
        return ""

    def create_peer_config(self, peer_private_key: str) -> str:
        """creates config for client and returns it as string"""
        cfg = (
            f"[Interface]\n"
            f"PrivateKey = {peer_private_key}\n"
            f"Address = {self.last_peer_adress}\n"
            f"DNS = 1.1.1.1\n\n"
            f"[Peer]\n"
            f"PublicKey = {self.server_public_key}\n"
            f"PresharedKey = {self.server_preshared_key}\n"
            f"AllowedIPs = 0.0.0.0/0\n"
            f"Endpoint = {self.server_ip}:{self.server_port}\n"
            f"PersistentKeepalive = 20"
        )
        return cfg

    def update_server_config(self, username: str, device: str) -> str:
        """adds new peer to config file and restarts wg-quick

        Args:
            username (str): username of new peer
            device (str): device of new peer

        Returns:
            str: config for new peer
        """
        user_priv_key, user_pub_key = self.generate_key_pair(username=username)

        self.add_new_peer(f"{username}_{device}", user_pub_key)
        # restart wg-quick
        self.restart_service()

        return self.create_peer_config(user_priv_key)

    def disconnect_peer(self, user_id: int):
        """Disconnects peer by user ID."""
        username = database.selector.get_username_by_id(user_id)

        self.comment_lines_under_username(username)

        # Restart wg-quick.
        self.restart_service()
        logger.info(f"[+] Peer {username} disconnected")

    def comment_lines_under_username(self, username: str):
        """Comments the 3 lines under the given username."""
        with open(self.cfg_path, "r+") as cfg:
            config = cfg.readlines()
            for line_index, line in enumerate(config):
                if line.startswith(f"#{username}"):
                    disconnected_username = f"DISCONNECTED_{line[1:]}"
                    config[line_index] = f"#{disconnected_username}"
                    for lines_under_username in range(line_index + 1, line_index + 4):
                        if lines_under_username < len(config) and not config[
                            lines_under_username
                        ].startswith("#"):
                            config[
                                lines_under_username
                            ] = f"#{config[lines_under_username]}"
            cfg.seek(0)
            cfg.write("".join(config))
            cfg.truncate()

    def reconnect_payed_user(self, user_id: int):
        """reconnects payed user by user_id"""
        username = database.selector.get_username_by_id(user_id)

        try:
            with open(self.cfg_path, "r") as cfg:
                config = cfg.read()
                for line in config.splitlines():
                    if line.startswith(f"#DISCONNECTED_{username}"):
                        config = config.replace(f"{line}\n", f"#{line[14:]}\n")

            with open(self.cfg_path, "w") as cfg:
                cfg.write(config)

            with open(self.cfg_path, "r") as cfg:
                config = cfg.read()
                config_as_list = config.splitlines()
                for line in config_as_list:
                    if line.startswith(f"#{username}"):
                        # get index of line with username
                        line_index = config.splitlines().index(line)
                        if config_as_list[line_index + 1].startswith("#[Peer]"):
                            for _ in range(3):
                                line_index += 1
                                config_as_list[line_index] = config_as_list[line_index][
                                    1:
                                ]

                config = "".join([f"{line}\n" for line in config_as_list])

            with open(self.cfg_path, "w") as cfg:
                cfg.write(config)
            # restart wg-quick
            self.restart_service()
            logger.info(f"[+] peer {username} reconnected")

        except Exception as e:
            logger.error(f"[-] {e}")
