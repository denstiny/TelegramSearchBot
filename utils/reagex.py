import re
import aiohttp
import urllib3
import re
from lxml import etree
from info import proxies,bt_icon,icon_list,PROXY_STATUS
from log import LOG
import asyncio
from async_lru import alru_cache


def title_text_cleanse(title: str):
    """ 清理开头 """
    text = re.sub(r'^\d+\.\s*', '', title)
    """ 清理结尾 """
    text = re.sub(r'\s*-?\s*\d+(\.\d+)?\s*[kK]?(?!\S)', '', text)
    return text

def check_url_is_channel(url: str):
    pattern = r'http[s]?://t.me/[^/]+/\d+$'
    match = re.search(pattern, url)
    if not match:
        return True
    else:
        return False

async def get_channel_number(url: str,num=0):
    if num > 3:
        return None
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    @alru_cache(maxsize=20 * 1000)
    async def get(url: str):
        #resulter = requests.get(url,proxies=proxies,verify=False).text
        async with aiohttp.ClientSession() as session:
            if PROXY_STATUS:
                async with session.get(url,proxy=proxies['http']) as resp:
                    return await resp.text()
            else:
                async with session.get(url) as resp:
                    return await resp.text()

    try:
        resulter = await get(url)
        lxhtml = etree.HTML(resulter,parser=etree.HTMLParser(encoding='utf-8'))
        text = lxhtml.xpath('//div[@class="tgme_page_extra"]')
        try:
            text = text[0].text
        except IndexError:
            return None

        pattern = r'^(\d+)\s+(\d+)?'
        matches = re.match(pattern, text)

        if matches:
            first_number = matches.group(1)
            second_number = matches.group(2) or None
            number = first_number
            if second_number:
                second_number = second_number[-1]
                number = f"{first_number}.{second_number}k"
            return number 
        else:
            return None
    except:
        LOG.warning("爬取群组信息失败,重新请求")
        get.cache_invalidate(url) # 索引失败说明并没有请求成功，清理这次的缓存
        await asyncio.sleep(3)
        return await get_channel_number(url,num+1)


def fenlen_url(text: str):
    if re.search(rf'{bt_icon["group"]}',text):
        return 2
    if re.search(rf'{bt_icon["channel"]}',text):
        return 3
    if re.search(rf'{bt_icon["image"]}',text):
        return 4
    if re.search(rf'{bt_icon["voice"]}',text):
        return 5
    if re.search(rf'{bt_icon["video"]}',text):
        return 6
    if re.search(rf'{bt_icon["message"]}',text):
        return 7
    if re.search(rf'{bt_icon["file"]}',text):
        return 7
    return None


def remove_special_characters(text):
    # 定义要移除的特殊字符的正则表达式模式
    pattern = r'[*_`~#<>]'
    # 使用 re.sub() 方法替换匹配到的特殊字符为空字符串
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

""" 对链接类型分类,排除无法分为的链接 """
def exterm_message(text:str):
    ts = text.split("\n")
    mlinks = []
    for s in ts:
        links = extract_links_from_markdown(s)
        for link in links:
            fen = fenlen_url(s)
            if fen:
                link.settype(fen)
                mlinks.append(link)
    return mlinks



def extract_links_from_markdown(markdown_text):
    pattern = r'\[([^\]]+)\]\((http[s]?://t\.me/[^\s?=&\)]+)\)'  # 匹配 [text](url) 形式的链接
    matches = re.findall(pattern, markdown_text)

    class base_links:
        text = ""
        url = ""
        m_type = 0
        def settype(self,n):
            self.m_type = n

        def __init__(self,text,url) -> None:
            self.text = text
            self.url = url

        def __str__(self) -> str:
            return f"{self.text} : {self.url}"

    links = [base_links(remove_special_characters(text),url) for text, url in matches]
    return links


def check_link_rules(message: str):
    pattern = re.compile(r'http[s]?://t\.me/[^\s?=&]+')
    match = re.search(pattern, message)
    if match:
        return True
    else:
        return False


def check_for_links(message):
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    # 使用正则表达式匹配链接
    matches = re.findall(pattern, message)
    # 如果匹配到链接，则返回 True，否则返回 False
    if matches:
        return True
    else:
        return False


def link_format(url,name) -> str:
    return f"<a href={url}>{name}</a>"

def message_format(m_type,title,url,people,keyboard):

    def add_itter_bold(match):
        char = match.group(0)
        return f"<p><strong><u>{char}</u></strong></p>"

    title = re.sub(keyboard,add_itter_bold,title,flags=re.IGNORECASE)
    if people:
        return f"{icon_list[m_type]} <a href=\"{url}\">{title}</a> {people}<br>"
    else:
        return f"{icon_list[m_type]} <a href=\"{url}\">{title}</a><br>"

def get_command_administrator(text: str):
    split_string = text.split()
    username = ""
    user_type = 0
    print(split_string,text)
    if len(split_string) == 2:
        username = split_string[0]
        user_type = split_string[1]
    elif len(split_string) == 1:
        username = split_string[0]
    else:
        return None
    return (username,user_type) if len(username) != 0 else  None


def get_command_link(text: str):
    pass

""" parse addlink command: return (url,title,weight) or None """
def parse_addlink_command(cond: str):
    LOG.info("解析url和weight")
    pattern = r"^(https?://\S+)(?:\s+(\d+))?$"
    match = re.match(pattern,cond)
    print(match)
    if match:
        url = match.group(1)
        weight = int(match.group(2) if  match.group(2) else 0)
        LOG.info(f"\nURL: {url}\nweight: {weight}")
        return (url,weight)
    else:
        LOG.info("解析失败")
        return None

def parse_setlink_command(cond:str):
    pattern = r"(.*?)\s+(.*?)\s+(\d+)$"  # 匹配 URL、标题和权重
    matches = re.match(pattern, cond)  # 进行匹配
    if matches:
        url = matches.group(1)
        title = matches.group(2)
        weight = matches.group(3)
        return (url,title,weight)
    else:
        return None


def group_format(name) -> str:
    return f"https://t.me/{name}"
