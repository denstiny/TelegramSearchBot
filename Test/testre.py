text = "🌐[👉旱涝保收双盈利模式：返水日结+负盈利免审👈](https://t.me/BTTY88888?ad=link937) 🌐[🔥瓦力飞投🔥国际视讯平台🔵百家乐🔴龙虎🟢炸金花💰秒充提💰](https://t.me/+1lk-en6WdkliNGI1) 🥇[清河社工库｜查档｜查人｜定位｜开房记录](https://t.me/qhsgk001/12) 🥈[铁山靠社工库|查人查档|手机定位|开房记录|冻结原因|](https://t.me/tsk0007/ad=kw4671) 🎖[免费社工库机器人/专注信息调查/个人信息/开房记录..](https://t.me/qwrrttry3) 📢[ 曝光台 - 反差婊 吃...](https://t.me/FCBBGT) 290k"


import utils.reagex
for link in utils.reagex.extract_links_from_markdown(text):
    if utils.reagex.check_url_is_channel(link.url):
        print(link.url)
