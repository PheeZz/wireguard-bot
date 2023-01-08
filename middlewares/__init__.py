from .Throttling import *
from loader import dp


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
