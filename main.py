from time import sleep
from core import client
import core
import manage
import info
from log import LOG
from multiprocessing import Process,Value


def acept_user(me_id):
    core.set_me(me_id.value)

    if info.PROXY_STATUS:
        LOG.info("设置代理")
        client.user.set_proxy(info.proxy)
    else:
        LOG.info("未启动代理")

    LOG.info("初始化监控端信号任务")
    manage.init_user_event(client.user)
    try:
        client.user_start()
        client.user_join()
    except KeyboardInterrupt:
        client.user_quit()

def acept_bot(me_id):
    if info.PROXY_STATUS:
        LOG.info("设置代理")
        client.bot.set_proxy(info.proxy)
    else:
        LOG.info("未启动代理")

    LOG.info("初始化响应端信号")
    manage.init_bot_event(client.bot)
    try:
        client.bot_start()
        me_id.value = core.asyncrun(core.me)
        client.bot_join()
    except KeyboardInterrupt:
        client.bot_quit()


if __name__ == "__main__":
    """ init logger """
    LOG.info("初始化日志")
    me_id = Value('i',0)
    bot_process = Process(target=acept_bot,args=(me_id,))
    bot_process.start()

    while me_id.value == 0:
        sleep(1)
    
    user_process = Process(target=acept_user,args=(me_id,))
    #user_process.start()

    bot_process.join()
    #user_process.join()
