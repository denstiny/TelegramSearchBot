from time import time
import math
import asyncio
from typing import List
from asyncache import cached
from cachetools import LRUCache, TTLCache
from telethon.sync import Button, TelegramClient
from telethon.sync import events
from telethon import events
from telethon.tl.types import InputUser, User,Channel
import database
import bisect
from info import CACHE_MAX
from utils.secureMap import secureMap
from database.mysql import  query_administrator_all
from log import LOG
from core.client import bot,user
from utils import reagex
import info
from telethon.errors import (
    FloodWaitError,
)


""" bot id """
BOTID = None

#afterSaveMap = secureMap()
#linkMap = secureMap() # 邀请链接
after_save_ceche = LRUCache(maxsize=CACHE_MAX)
STATUS_MAP = TTLCache(ttl=9000,maxsize=CACHE_MAX*100)
search_cache = TTLCache(ttl=9000,maxsize=CACHE_MAX*100)

async def get_cache_key(event):
    chat = event.chat if event.chat else (await event.get_chat())
    if not chat: return
    cache_key = ""
    if event.is_channel:
        pass
    if event.is_private:
        cache_key = f'{chat.id}_{event._message_id}'
    if event.is_group:
        cache_key = f'{chat.id}_{event.from_id.user_id}_{event._message_id}'
    return cache_key

async def get_query_callback_user(event):
    user_id = ""
    if isinstance(event,events.CallbackQuery.Event):
        if event.is_group:
            user_id = f"{event.original_update.user_id}"
        elif event.is_private:
            user_id = f"{event.original_update.user_id}"
    return user_id



async def get_user_id(event):
    chat = event.chat if event.chat else (await event.get_chat())
    if not chat: return
    chat_id = ""
    if event.is_channel:
        pass
    if event.is_private:
        chat_id = f'{chat.id}'
    if event.is_group:
        chat_id = f'{event.from_id.user_id}'
    return chat_id

async def get_user_name(event):
    chat = event.chat if event.chat else (await event.get_chat())
    if not chat: return
    username = ""
    if event.is_channel:
        pass
    if event.is_private:
        username = f'{chat.username}'
    if event.is_group:
        username = f'{event.from_id.username}'
    return username


#cacheuersearch = secureMap()

class PaginationModel():
    def __init__(self,all_items,key: str):
        self.all_items = {}
        self.m_type = info.BTNALL
        for m_type in info.btn_sort:
            self.all_items[m_type] = []

        for item in all_items:
            source = item['_source']
            tem = database.linkage(title=source['title'],
                                   url = source['url'],
                                   weight = source['widget'],
                                   people = source['people'],
                                   m_type = source['m_type'],
                                   score=item['_score'])

            bisect.insort_left(self.all_items[info.BTNALL],tem,key=lambda x: x.score + x.weight)
            m_type = info.icon_type[tem.m_type]
            bisect.insort_left(self.all_items[m_type],tem,key=lambda x: x.score + x.weight)

        #for value in self.all_items[info.BTNALL]:
        #    LOG.info(f"{value.title} {value.score + value.weight}")

        self._current_page = 0
        self.keyboard = key
        self.create_time = time()
        self._count = len(all_items)

    def get_type_count(self,type):
        if type in self.all_items:
            return len(self.all_items[type])
        return 0

    def set_type(self,_type):
        self._current_page = 0
        self.m_type = _type
    
    def createtime(self):
        return self.create_time

    """ 添加页"""
    def addpage(self,page: database.linkage):
        self.all_items[info.BTNALL].append(page)

        if page.m_type in self.all_items:
            #self.all_items[page.m_type].append(page)
            bisect.insort_left(self.all_items[info.BTNALL],page,key=lambda x: x.score + x.weight)
        else:
            self.all_items[page.m_type] = [page]

    """ 获取制定页 """
    def get_page(self,n):
        if n > self.count():
            return None
        else:
            s,e = self._get_index(n)
            return self.build_page_text(s,e)

    """ 获取当前所在页码 """
    def set_current_page(self,n):
        if n > self.count() - 1:
            return
        self._current_page = n

    """ 获取当前所在页码 """
    def get_current_page(self):
        return self._current_page
    
    """ 下一页 """
    def next(self):
        self._current_page += 1
        if self._current_page > self.count() - 1:
            self._current_page -= 1
            return None

    # 计算第n页的开始索引和结束索引
    def _get_index(self,n):
        _count = self.count()
        start_index = self._current_page * info.page_title_max
        end_index = min( (n + 1) * info.page_title_max, _count)
        return start_index,end_index

    def build_page_text(self,_start,_end) -> str:
        text = ""
        all_items = []
        if self.m_type in self.all_items:
            all_items = self.all_items[self.m_type]
        else:
            return ""


        for n in range(_start,_end):
            item = all_items[n]
            text += reagex.message_format(item.m_type,
                                          item.title,
                                          item.url,
                                          item.people,
                                          self.keyboard) + "\n"
        return text

    """ 获取当前页 """
    def current(self):
        s,e = self._get_index(self._current_page)
        return self.build_page_text(s,e)

    """ 上一页 """
    def prev(self):
        self._current_page -= 1
        if self._current_page < 0:
            self._current_page += 1
            return None

    """ 统计当前页码数量 """
    def count(self):
        if self.m_type in self.all_items:
            return len(self.all_items[self.m_type])
        else:
            return 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index > len(self.all_items)-1:
            raise StopIteration

        value = None
        value = self.all_items[self.m_type][self.index]
        self.index += 1
        return value

def build_bot_message_buttons(user_id: str,cache_key: str,pagintion: PaginationModel,lv = info.BTNALL):
    def build_btn(mes: str, n = None):
        text = f'{user_id} {cache_key} {mes}'.encode('utf-8')
        if n != None:
            return Button.inline(f"{info.bt_icon[mes]}({n})",text)
        return Button.inline(f"{info.bt_icon[mes]}",text)

    switch_page_btn = [] # 切换页面按钮
    if math.floor(pagintion.count() / info.page_title_max) -1 > 1:
        if pagintion.get_current_page() != 0:
            switch_page_btn.append(build_btn(info.BTNLAST))

        if pagintion.get_current_page() < math.floor(pagintion.count()  / info.page_title_max)-1:
            switch_page_btn.append(build_btn(info.BTNNEXT))
    
    switch_type_btn = [] # 切换分类按钮
    for item in info.btn_sort:
        _count = pagintion.get_type_count(item)
        if lv != item and _count > 0:
            switch_type_btn.append(build_btn(item,_count))

    return [switch_page_btn,
            switch_type_btn]

""" 加载管理员列表 """
async def load_administrator():
    administrators = query_administrator_all()
    if administrators != []:
        return administrators

def set_me(id):
    global BOTID
    BOTID = id

async def me():
    global BOTID
    if not BOTID:
       me = await bot.get_me()
       if isinstance(me,InputUser):
           BOTID = me.user_id
           return BOTID
       elif isinstance(me,User):
           BOTID = me.id
           return BOTID
       else:
           return
    else:
        return BOTID

@cached(LRUCache(maxsize=CACHE_MAX))
async def get_entity(url: str):
    try:
        await user.get_dialogs()
        channel_entity = await user.get_entity(url)
        if isinstance(channel_entity,Channel):
            return channel_entity
    except FloodWaitError as e:
        LOG.error(f"被限制获取实体,等待{e.seconds}秒.")
        return
    except Exception as e:
        LOG.error(f"查询链接错误{url}: {e}")
        return

def get_channel_username(channel: Channel):
    list = []
    if channel.username:
        list.append(channel.username)
    elif channel.usernames != []:
        if channel.usernames == None:
            return list
        for username in channel.usernames:
            list.append(username.username)
    return list


@cached(LRUCache(maxsize=CACHE_MAX))
async def build_bot_reply_message(message):
    """ 查询数据 """
    result = await database.query(message)
    if result:
        """ 构建消息 """
        m = PaginationModel(result,message)
        return m
    return None


def asyncrun(fun):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(fun())
