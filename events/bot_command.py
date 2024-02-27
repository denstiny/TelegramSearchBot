from telethon.sync import events
import database
#from utils.secureMap import secureMap
from core import get_channel_username, get_entity, get_user_id, get_user_name,STATUS_MAP
from utils import reagex
from log import LOG
from database import mysql

_command_list = []

def BUILD_COMMAND(command):
    if not command:
        return events.NewMessage(func=lambda e: e.is_private)
    command = f"/{command}"
    _command_list.append(command)
    return events.NewMessage(pattern=command,func=lambda e: e.is_private)

async def callbacks(event: events.newmessage.NewMessage.Event):
    user_id = await get_user_id(event)
    if event.text in _command_list:
        return
    try:
        status = STATUS_MAP.get(user_id)
        text = ""
        if status:
            if status == "ADDADMINISTRATOR": # 添加管理员
                chat = event.chat if not event.chat else await event.get_chat()
                username = chat.username
                query_result = await mysql.query_administrator(keyboard=username)
                if query_result != []:
                    result = reagex.get_command_administrator(event.message.message)
                    if not result:
                        text = "添加管理员错误"
                    else:
                        username,m_tyep = result
                        await mysql.insert_table_administrator(username,m_tyep)
                        text = "尊敬的管理员用户，您已成功添加新的管理员"
                else:
                    text = "非管理员用户无法添加"
            elif status == "DELADMINISTRATOR": # 删除管理员
                chat = event.chat if not event.chat else await event.get_chat()
                username = chat.username
                query_result = await mysql.query_administrator(keyboard=username)
                if query_result != []:
                    result = reagex.get_command_administrator(event.message.message)
                    if not result:
                        text = "删除管理员错误"
                    else:
                        username,m_type = result
                        if not await mysql.del_administrator(username):
                            text = "未找到要删除的用户"
                        else:
                            text = "删除成功"
                else:
                    text = "非管理员无权所使用该命令"
            elif status == "ADDLINK": # 添加链接
                chat = event.chat if not event.chat else await event.get_chat()
                username = chat.username
                query_result = await mysql.query_administrator(keyboard=username)
                if query_result != []:
                    LOG.info("处理addlink指令回调")
                    LOG.info(event.message.message)
                    parse = reagex.parse_addlink_command(event.message.message)
                    if parse:
                        url,weight = parse
                        LOG.info(f"{url} -> {weight}")
                        people = await reagex.get_channel_number(url)
                        LOG.info(f"{url} -> {people}")
                        channel = await get_entity(url)
                        if channel:
                            m_type = 0
                            if channel.broadcast:
                                m_type = 3
                            elif channel.megagroup:
                                m_type = 2
                            url = reagex.group_format(get_channel_username(channel)[0])
                            await database.appen_index(title=channel.title,
                                                       url=url,
                                                       people=people,
                                                       weight=weight,
                                                       m_type=m_type)
                            text = "推送成功，等待管理员审核"
                        else:
                            text = "错误的群组链接"
                        #database.insert_table_linkage()
                    else:
                        text = "错误的群组/频道链接"
                else:
                    text = "非管理员用户无权访问该指令"
            elif status == "DELLINK": # 删除链接
                if reagex.check_link_rules(event.message.message):
                    username = await get_user_name(event)
                    if username and await mysql.query_administrator(username):
                        if await database.del_data(event.message.message):
                            text = "删除链接成功"
                        else:
                            text = "无法删除该链接"
                    else:
                        text = "非管理员用户无权使用该指令"
                else:
                    text = "错误的链接"
            elif status == "SETLINK": # 设置链接
                chat = event.chat if not event.chat else await event.get_chat()
                username = chat.username
                query_result = await database.query_administrator(keyboard=username)
                if query_result != []:
                    LOG.info("处理dellink指令回调")
                    LOG.info(event.message.message)
                    parse = reagex.parse_setlink_command(event.message.message)
                    if parse:
                        url,title,weight = parse
                        LOG.info(f"{url} -> {weight}")
                        LOG.info(f"{url} -> {title}")
                        if await database.update_table_linkage(url,title,weight):
                            text = "修改链接成功"
                        else:
                            text = "修改链接失败"
                    else:
                        text = "命令格式错误"
                else:
                    text = "非管理员用户您无法访问该命令"
            else:
                return
        else:
            return
        await event.reply(text)
        return text
    except:
        await event.reply("命令查询失败")

def after_execution(another_function):
    def decorator(async_func):
        async def wrapper(*args, **kwargs):
            result = await async_func(*args, **kwargs)
            await another_function(*args,**kwargs)
            return result
        return wrapper
    return decorator

""" 开始指令 """
async def start(event: events.newmessage.NewMessage.Event):
    LOG.info(f"command: start {event.chat_id}")
    await event.respond("发送关键词来寻找群组、频道或机器人。\n\n👉 <a href=\"tg://setlanguage?lang=zhcncc\">点这里安装【简体中文】</a>👈")
    await event.respond("/help - 帮助\n/administrator - 管理员列表\n/addlink - 添加链接\n/setlink - 设置链接\n/dellink - 删除链接\n/addadministrator - 添加管理员\n/deladministrator - 删除管理员")
    STATUS_MAP[await get_user_id(event)] = "QUERY"

""" 帮助指令 """
async def help(event: events.newmessage.NewMessage.Event):
    await event.reply("/help - 帮助\n/administrator - 管理员列表\n/addlink - 添加链接\n/setlink - 设置链接\n/dellink - 删除链接\n/addadministrator - 添加管理员\n/deladministrator - 删除管理员")

""" 管理员列表指令 """
async def administrator(event: events.newmessage.NewMessage.Event):
    adminlist = await database.query_administrator_all()
    if adminlist != []:
        text = "--- **管理员列表** ---\n"
        for user in adminlist:
            #text += reagex.link_format(f"https://t.me/{user.user}",user.user) + user.m_type
            text += f"{reagex.link_format(f'https://t.me/{user.user}',user.user)} 权限等级: {user.m_type}\n"
        await event.reply(text,link_preview=False)
    else:
        await database.insert_table_administrator("Dens_Tiny",100)
        adminlist = await database.query_administrator_all()
        text = ""
        for user in adminlist:
            text += f"{reagex.link_format(f'https://t.me/{user.user}',user.user):<10} 权限等级: {user.m_type}\n"
        await event.reply(text,link_preview=False)

""" 添加链接 """
async def addlink(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "ADDLINK"
    await event.reply("请按实例输入参数(管理员可用):\n{链接} {权重(非超级管理员请不要输入0)}")

""" 设置链接 """
async def setlink(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "SETLINK"
    await event.reply("请按实例输入参数(非管理员无法使用):\n{链接} {标题} {权重(非超级管理员请输入0)}")

""" 删除链接 """
async def dellink(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "DELLINK"
    await event.reply("请按实例输入参数(非超级管理员无法使用):\n{链接}")

""" 添加管理员 """
async def addadministrator(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "ADDADMINISTRATOR"
    await event.reply("请按实例输入参数(非超级管理员无法使用):\n{@用户名}")

""" 删除管理员 """
async def deladministrator(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "DELADMINISTRATOR"
    await event.reply("请按实例输入参数(非超级管理员无法使用):\n{用户名}")


""" 搜索 """
async def query(event: events.newmessage.NewMessage.Event):
    STATUS_MAP[await get_user_id(event)] = "QUERY"
    await event.reply("发送关键词来寻找群组、频道,消息或机器人。")
