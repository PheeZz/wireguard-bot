"""Finite state machine classes module
    """

from aiogram.dispatcher.filters.state import State, StatesGroup


class New_config(StatesGroup):
    device = State()
