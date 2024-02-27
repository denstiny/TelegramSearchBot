from telethon import events
from telethon.sync import Button
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon.tl.types import Channel, User
import core
from log import LOG
import info

async def handler(event: events.callbackquery.CallbackQuery.Event):
    text = event.data.decode('utf-8')
    chat = event.chat if event.chat else (await event.get_chat())
    if not chat: return
    user_id,key,m_type = text.split(" ")
    c_user_id = await core.get_query_callback_user(event)
    if c_user_id != user_id:
        await event.respond(f'无法操作他人的面板 {text}')
        return
    m = core.search_cache.get(key)
    if isinstance(m,core.PaginationModel):
        
        buttons = []
        if m_type == info.BTNLAST: # 下一页
            m.prev()
            buttons = core.build_bot_message_buttons(user_id,key,m)
        elif m_type == info.BTNNEXT: # 上一页
            m.next()
            buttons = core.build_bot_message_buttons(user_id,key,m)
        elif m_type in [info.BTNGROUP,
                        info.BTNCHANNEL,
                        info.BTNIMAGE,
                        info.BTNVOICE,
                        info.BTNVIDEO,
                        info.BTNADVERTI,
                        info.BTNMESSAGE,
                        info.BTNFILE,
                        info.BTNALL]: # 切换类型
            m.set_type(m_type)
            buttons = core.build_bot_message_buttons(user_id,key,m,m_type)
        else:
            return

        try:
            await event.edit(f"{m.current()}",buttons = buttons,link_preview=False)
        except MessageNotModifiedError:
            pass
    else:
        await event.edit(f"消息已过期")
