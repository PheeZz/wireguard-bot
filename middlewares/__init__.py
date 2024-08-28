from loader import dp

from .Throttling import *


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
