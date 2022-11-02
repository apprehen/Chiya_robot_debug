import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
)
from nonebot import on_keyword
from nonebot.adapters import Bot,Event
import requests
import time
from services.log import logger

__zx_plugin_name__ = "今日新番"
__plugin_usage__="""
usage:
    不知道什么时候有番看？
    指令:
        今日新番，今日番剧
        示例:今日新番
            :今日番剧
""".strip()
__plugin_des__="看番捏"
__plugin_cmd__=["今日新番","今日番剧","今日动画"]
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["今日新番", "今日番剧", "今日动画"],
}
__plugin_version__ = 0.1
__plugin_author__ = " yueyun "

updatefan = nonebot.on_keyword({'今日番剧','今日新番','今日动画'})
@updatefan.handle()
async def _(bot: Bot, event: MessageEvent):
    msg = await spiderfan()
    await updatefan.send(Message(msg))

async def spiderfan():
    day = time.localtime(time.time())
    thistime = str(day.tm_mon) + '-' + str(day.tm_mday)
    anime_list = requests.get("https://api.bilibili.com/pgc/web/timeline?types=1&before=6&after=6").json()['result']
    i_list = []
    anime = ''
    for i in anime_list:
        if i['date'] == thistime:
            i_list = i['episodes']
    for it in i_list:
        url = it['ep_cover']
        anime += it['pub_time'] + '  更新  ' + it['title'] + '  ' + it['pub_index'] +'\n' + f'[CQ:image,file={url}]' + '\n' +'--------------------------' + '\n'
    return anime

