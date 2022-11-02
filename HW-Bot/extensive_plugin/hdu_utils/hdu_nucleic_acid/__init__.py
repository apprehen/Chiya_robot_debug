import json
import time
import datetime
import aiofiles


import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot import Driver
from utils.http_utils import AsyncHttpx
from configs.path_config import TEMP_PATH
from services.log import logger
from utils.message_builder import image


driver: Driver = nonebot.get_driver()
# 插件信息
__zx_plugin_name__ = "杭电核酸直播"
__plugin_usage__ = """
usage：
    指令：
        查看核酸排队情况/核酸
        返回最近的核酸队伍照片
        核酸直播
        返回核酸直播的链接
    ps: 妈妈再也不用担心我核酸排队了！
    接口来源：HDUHELP
""".strip()
__plugin_des__ = "HDU实时核酸排队情况！"
__plugin_cmd__ = ["查看核酸排队情况", "核酸直播", "核酸"]
__plugin_version__ = 0.1
__plugin_author__ = "Lycoiref"
__plugin_type__ = ("杭电生活", )
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["查看核酸排队情况", "核酸直播", "核酸"],
}


last_pic = on_command("核酸直播", aliases={"核酸"}, priority=5, block=True)


@last_pic.handle()
async def _(bot: Bot, event: MessageEvent):
    today = datetime.date.today()
    info_url = 'https://api.metaspace.mjclouds.com/v1/info'
    info_list = await AsyncHttpx.get(info_url)
    info_list = json.loads(info_list.text)
    lives = info_list['data']['live']
    has_live = True
    try:
        live = lives[0]
    except IndexError:
        await last_pic.finish("暂无直播")
        has_live = False
    print(live['ID'])

    # 获取今天00:00的时间戳
    today_00 = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    today_00_timestamp = int(time.mktime(today_00.timetuple())) * 1000
    print(today_00_timestamp)

    # 获取今天中午12:00的时间戳
    today_12 = datetime.datetime(today.year, today.month, today.day, 12, 0, 0)
    today_12_timestamp = int(time.mktime(today_12.timetuple())) * 1000
    print(today_12_timestamp)

    # 获取今天晚上18:00的时间戳
    today_18 = datetime.datetime(today.year, today.month, today.day, 18, 0, 0)
    today_18_timestamp = int(time.mktime(today_18.timetuple())) * 1000
    print(today_18_timestamp)

    # 获取当前时间的时间戳
    now = datetime.datetime.now()
    now_timestamp = int(time.mktime(now.timetuple())) * 1000

    data = {
        'EndTime': now_timestamp,
        'StartTime': today_00_timestamp,
        'LiveID': live['ID'],
        'NextStartTime': '',
    }

    res = await AsyncHttpx.post('https://api.metaspace.mjclouds.com/v1/snap', json=data)
    res = json.loads(res.text)
    if res['code'] == 20000:
        logger.info(f"请求核酸直播成功")
    img = await AsyncHttpx.get(res['data']['Snaps'][0]['Url'])
    # 将图片保存到缓存文件夹
    async with aiofiles.open(
        TEMP_PATH / f"{now_timestamp}.jpg", "wb"
    ) as f:
        await f.write(img.content)
    msg = image(TEMP_PATH / f"{now_timestamp}.jpg")
    await last_pic.finish(msg)
