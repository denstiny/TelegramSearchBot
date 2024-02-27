import os
import sys
#from loguru import logger

""" info log file path """
PROJECT_ROOT = os.path.dirname(sys.argv[0])
PROJECT_LOG = f"{PROJECT_ROOT}/log/telegarmbot.log"
#logger.add(f"{PROJECT_ROOT}/log/telegarmbot.log",
#           level="DEBUG",
#           format="{time} - {level} - {message}"
#)

""" info bot token """
bot_token = ""
zhilianbot_token = ""

""" info proxy url """
http_proxy_url = 'http://127.0.0.1:7890'

""" proxy """
PROXY_STATUS = os.environ.get("PROXYSTATUS")

proxy = ("socks5", "127.0.0.1",7891)
proxies = {'http': 'http://127.0.0.1:7890',
           'https': 'http://127.0.0.1:7890'}


""" session name """
session_name = "Denstiny"

"""API ID"""
api_id = 0
bot_id = 0

"""API HASH"""
api_hash = ""
bot_hash = ""


"""Button icon"""
icon_list = ["➡︎","⬅︎","👥","📢","🏞","🎧","🎬","💬","📁","🌐"]

"""Button icon"""
BTNNEXT = "next"
BTNLAST = "last"
BTNGROUP = "group"
BTNCHANNEL = "channel"
BTNIMAGE = "image"
BTNVIDEO = "video"
BTNVOICE = "voice"
BTNMESSAGE = "message"
BTNFILE = "file"
BTNADVERTI = "adverti"
BTNALL = "all"

icon_list = ["➡︎","⬅︎","👥","📢","🏞","🎧","🎬","💬","📁","🌐"]
bt_icon = {
    BTNNEXT: icon_list[0],
    BTNLAST: icon_list[1],
    BTNGROUP: icon_list[2],
    BTNCHANNEL: icon_list[3],
    BTNIMAGE: icon_list[4],
    BTNVOICE: icon_list[5],
    BTNVIDEO: icon_list[6],
    BTNMESSAGE: icon_list[7],
    BTNFILE: icon_list[8],
    BTNADVERTI: icon_list[9] ,
    BTNALL : "全部"
    }

icon_weight = { bt_icon[BTNGROUP] : 1,
               bt_icon[BTNCHANNEL]: 1,
               bt_icon[BTNVIDEO]: 2,
               bt_icon[BTNMESSAGE]: 1,
               bt_icon[BTNIMAGE]: 0,
               bt_icon[BTNADVERTI]: 0,
               bt_icon[BTNVOICE]: 0,
               bt_icon[BTNFILE]: 0}

icon_type = [ 
    BTNNEXT,
    BTNLAST,
    BTNGROUP,
    BTNCHANNEL,
    BTNIMAGE,
    BTNVOICE,
    BTNVIDEO,
    BTNMESSAGE,
    BTNFILE,
    BTNADVERTI,
    BTNALL]

btn_sort = [BTNALL,
            BTNCHANNEL,
            BTNGROUP,
            BTNVIDEO,
            BTNMESSAGE,
            BTNVOICE,
            BTNIMAGE,
            BTNFILE,
            BTNADVERTI]

""" page: 20 """
page_title_max = 20

""" database """
MYSQL_DATABASE = "Telegram"
ES_INDEX = "telegram"

""" cache """
CACHE_MAX = 5000
