from telethon import events
from core import client, me
from telethon.tl.types import Channel, User
import core
from log import LOG
from utils import reagex
#from database.mysql import insert_table_linkage
import database
from info import icon_weight,icon_list

async def handler(event):
    if await me() == event.message.chat_id:
        LOG.info("排除自己发出的消息")
        return
    text = event.text
    for link in reagex.exterm_message(text):
        #channel = reagex.check_url_is_channel(link.url)
        if not core.after_save_ceche.get(link.url,None):
            number = await reagex.get_channel_number(link.url)
            await database.appen_index(title = reagex.title_text_cleanse(link.text),
                                       people = number,
                                       url = link.url,
                                       m_type=link.m_type,
                                       weight=0)
            core.after_save_ceche[link.url] = True
        else:
            LOG.warning(f"{link.text} 重复链接")
