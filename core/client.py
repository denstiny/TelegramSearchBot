from telethon import TelegramClient, events,functions
import info
from log import LOG
user = TelegramClient(info.session_name,
                        info.api_id,
                        info.api_hash)



""" bot """
bot = TelegramClient('bot',
                        info.api_id,
                        info.api_hash)

bot.parse_mode = "html"

def user_start():
    LOG.info("启动监控端")
    user.start()

def bot_start():
    LOG.info("启动响应端")
    bot.start(bot_token=info.bot_token)

def user_join():
    LOG.info("等待监控端任务循环")
    user.run_until_disconnected()

def bot_join():
    LOG.info("等待响应端任务循环")
    bot.run_until_disconnected()

def user_quit():
    LOG.info("正在退出监控端任务")
    try:
        user.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        user.loop.close()

def bot_quit():
    LOG.info("正在退出响应端任务")
    try:
        bot.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bot.loop.close()
