from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import configuration
from utils.vpn_cfg_work import WireguardConfig

bot = Bot(token=configuration.WG_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
vpn_config = WireguardConfig()
