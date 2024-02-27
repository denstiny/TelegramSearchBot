from telethon import TelegramClient, events,functions
from events import user_accept_message
from events import bot_command
from events import bot_command,bot_querycallback,bot_query,bot_command

def init_user_event(user: TelegramClient):
    user.add_event_handler(user_accept_message.handler,events.NewMessage())
    user.add_event_handler(user_accept_message.handler,events.MessageEdited())


def init_bot_event(bot: TelegramClient):
    bot.add_event_handler(bot_query.handler,events.NewMessage())
    bot.add_event_handler(bot_querycallback.handler,events.CallbackQuery())
    """ 用户命令 """
    bot.add_event_handler(bot_command.start,bot_command.BUILD_COMMAND("start"))
    bot.add_event_handler(bot_command.administrator,bot_command.BUILD_COMMAND("administrator"))
    bot.add_event_handler(bot_command.help,bot_command.BUILD_COMMAND("help"))
    bot.add_event_handler(bot_command.query,bot_command.BUILD_COMMAND("query"))
    bot.add_event_handler(bot_command.addlink,bot_command.BUILD_COMMAND("addlink"))
    bot.add_event_handler(bot_command.setlink,bot_command.BUILD_COMMAND("setlink"))
    bot.add_event_handler(bot_command.dellink,bot_command.BUILD_COMMAND("dellink"))
    bot.add_event_handler(bot_command.addadministrator,bot_command.BUILD_COMMAND("addadministrator"))
    bot.add_event_handler(bot_command.deladministrator,bot_command.BUILD_COMMAND("deladministrator"))
    bot.add_event_handler(bot_command.callbacks,bot_command.BUILD_COMMAND(command=None))
