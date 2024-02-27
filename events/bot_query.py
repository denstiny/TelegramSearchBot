from telethon import events
import core
from log import LOG
from utils import reagex
import database
from events.bot_command import STATUS_MAP

async def handler(event: events.newmessage.NewMessage.Event):
    rawtext = event.text
    if rawtext[0] == '/':
        return
    user_id = await core.get_user_id(event)
    if not user_id: return
    status = STATUS_MAP.get(user_id)
    if status and status != "QUERY":
        LOG.info(f"无法查询,当前处于命令等待响应 {status}")
        return

    if reagex.check_for_links(rawtext):
        await event.reply(f"触发违禁词:\n无法搜索链接")
        return

    chat = event.chat if event.chat else (await event.get_chat())
    if not chat: return

    username = await core.get_user_name(event)
    LOG.critical(f"用户: {username} 查询: `{event.message.message}`")

    message = await core.build_bot_reply_message(event.message.message)

    buttons = []
    if message:
        """ 构建响应消息 """
        #m = core.PaginationModel(result,rawtext)
        """ 缓存到缓冲区 """
        cache_key = await core.get_cache_key(event)
        if not cache_key: return
        core.search_cache[cache_key] = message

        """ 构建按钮 """
        buttons = core.build_bot_message_buttons(user_id,cache_key,message)
        if buttons != []:
            await event.reply(message.current(),link_preview=False,buttons = buttons)
            LOG.critical(f"用户: {username} 请求 `{event.message.message}` 完成响应 {message.count()} 条数据")
        else:
            await event.reply(message.current(),link_preview=False)
            LOG.critical(f"用户: {username} 请求 `{event.message.message}` 完成响应 {message.count()} 条数据")
    else:
        await event.reply(f"用户 {username} 请求 `{event.message.message}` 查询得到空数据")
