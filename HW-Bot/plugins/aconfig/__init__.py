from utils.message_builder import image
from configs.path_config import IMAGE_PATH
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from utils.utils import FreqLimiter
from configs.config import NICKNAME
import random
from nonebot import on_keyword
import os


__zx_plugin_name__ = "基本设置 [Hidden]"
__plugin_usage__ = "用法： 无"
__plugin_version__ = 0.1
__plugin_author__ = 'HibiKier'


_flmt = FreqLimiter(300)


config_play_game = on_keyword({"打游戏"}, permission=GROUP, priority=1, block=True)


@config_play_game.handle()
async def _(event: GroupMessageEvent):
    if not _flmt.check(event.group_id):
        return
    _flmt.start_cd(event.group_id)
    await config_play_game.finish(
        image(random.choice(os.listdir(IMAGE_PATH / "dayouxi")), "dayouxi")
    )


self_introduction = on_command(
    "自我介绍", aliases={"介绍", "你是谁", "你叫什么"}, rule=to_me(), priority=5, block=True
)


@self_introduction.handle()
async def _():
    if NICKNAME.find('Chiya') != -1:
        result = (
            "我叫Chiya\n"
            "擅长做各式各样的和果子，平时最大的兴趣是把刚研发完成的新和果子取名字。\n"
            "高中一年级学生，日式甜点屋甘兔庵的女儿，和心爱是同班同学。\n"
            "身高嘛，身高是什么\n"
            "我生日是9月19日\n"
            # "最好的朋友是椛！\n" + image("zhenxun")
        )
        await self_introduction.finish(result)


my_wife = on_keyword({"老婆"}, rule=to_me(), priority=5, block=True)


@my_wife.handle()
async def _():
    await my_wife.finish(image("laopo.jpg", "other"))

