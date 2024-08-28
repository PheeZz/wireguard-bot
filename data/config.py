from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Literal


class Config(BaseSettings):
    # MODE: Literal["DEV", "TEST", "PROD"]
    # LOG_LEVEL: str
    WG_BOT_TOKEN: str
    WG_SERVER_PORT: int
    # WG_SERVER_PUBLIC_KEY:...
    # WG_SERVER_PRESHARED_KEY:...
    WG_CFG_PATH: str
    ADMINS_IDS: str
    PAYMENT_CARD: str
    CONFIGS_PREFIX: str
    BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES: int
    PEER_DNS: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def ASYNC_DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=False)

    @property
    def WG_SERVER_PUBLIC_KEY(self):
        self._server_public_key = ...
        with open("/etc/wireguard/wg0.conf"):
            ...
