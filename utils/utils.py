from aiogram.types import Message, CallbackQuery


def cmd_cleaner(message: Message) -> Message:
    """cleans message.text from commands

    Args:
        message (Message): message object from aiogram

    Returns:
        message: message object from aiogram
    """
    _map = {
        "/command": "",
        "/other_command": "",
        "@botname_bot": "",
        "/": "",
    }
    for key, value in _map.items():
        message.text = message.text.replace(key, value)
    message.text = message.text.lower().strip()
    return message


def get_appeal(call: CallbackQuery) -> str:
    """returns appeal for user

    Args:
        call: CallbackQuery object from aiogram

    Returns:
        str: appeal for user
    """
    return call["from"]["first_name"] or call["from"]["username"]
