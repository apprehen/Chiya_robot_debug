import asyncio
import datetime
import os
import random


import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, GroupMessageEvent
from nonebot.params import Command
from nonebot import Driver
from utils.http_utils import AsyncHttpx
from configs.path_config import RECORD_PATH
from utils.message_builder import record
from utils.utils import scheduler, get_bot
from services.log import logger
from typing import Tuple
from .._models import HDU_Sign_User
from ..get_session import get_session


driver: Driver = nonebot.get_driver()
# 插件信息
__zx_plugin_name__ = "杭电课表"
__plugin_usage__ = """
usage：
    绑定杭电通行证指令（私聊！！！）：
        set hdu username password
    栗子：set hdu 20181111 123456
    指令集：
        今日课表
        明日课表
        订阅课表推送/关闭课表推送
    待添加指令集：
        本周课表
""".strip()
__plugin_des__ = "是HDU的课表插件！"
__plugin_cmd__ = ["今日课表"]
__plugin_version__ = 0.5
__plugin_author__ = "Lycoiref"
__plugin_type__ = ("杭电生活", )
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["今日课表"],
}


today_schedule = on_command("今日课表", aliases={"明日课表"}, priority=5, block=True)
push_course = on_command("订阅课表推送", priority=5, block=True)
close_push = on_command("关闭课表推送", priority=5, block=True)
test_command = on_command("test_hdu", priority=5, block=True)


@today_schedule.handle()
async def _(bot: Bot, event: MessageEvent, cmd: Tuple[str, ...] = Command()):
    try:
        courses = await get_schedule(event.user_id)
    except Exception as e:
        logger.error(f"获取课表失败，原因为{e}")
        await today_schedule.finish("获取课表失败，请稍后再试")
    res_msg = "今日课表如下:\n"
    today_courses = []
    week = await get_week()
    for course in courses:
        # 获取今天星期几
        today = datetime.datetime.now().weekday() + 1
        # 判断指令是今日课表还是明日课表
        if cmd[0] == "明日课表":
            today += 1
            res_msg = "明日课表如下:\n"
        if course["weekDay"] == today:
            # 判断本周是否有这节课
            startWeek = course["startWeek"]
            endWeek = course["endWeek"]
            if startWeek <= week <= endWeek:
                # 判断是否是单双周
                if course["period"]:
                    if course["period"] == "单" and week % 2 == 0:
                        continue
                    elif course["period"] == "双" and week % 2 == 1:
                        continue
                # 将课程信息添加到列表中
                today_courses.append(course)
    # 按照课程开始时间排序
    today_courses.sort(key=lambda x: x["startSection"])
    for course in today_courses:
        res_msg += f"{course['courseName']}\n"
        res_msg += f"时间：第{course['startSection']}-{course['endSection']}节\n"
        res_msg += f"地点：{course['classRoom']}\n"
        res_msg += f"教师：{course['teacherName']}\n"
        res_msg += "----------------\n"
    await today_schedule.finish(res_msg + "加油，今天又是元气满满的一天！")

    
@push_course.handle()
async def _(bot: Bot, event: MessageEvent):
    await HDU_Sign_User.set_course_auto_push(event.user_id, True)
    await push_course.finish("已成功订阅课表推送")


@close_push.handle()
async def _(bot: Bot, event: MessageEvent):
    await HDU_Sign_User.set_course_auto_push(event.user_id, False)
    await close_push.finish("已成功关闭课表推送")


@test_command.handle()
async def _(bot: Bot, event: MessageEvent):
    voice, msg = await get_voice()
    await test_command.send(msg)
    # await test_command.finish(voice)
    await bot.send_private_msg(user_id=event.user_id, message=voice)


@test_command.handle()
async def _(bot: Bot, event: MessageEvent):
    voice, msg = await get_voice()
    await test_command.send(msg)
    # await test_command.finish(voice)
    await bot.send_private_msg(user_id=event.user_id, message=voice)


# 早上6:50定时推送课表
@scheduler.scheduled_job('cron', hour=6, minute=50)
async def _():
    bot = get_bot()
    # 获取所有绑定了杭电课表的用户
    users = await HDU_Sign_User.get_all_users(False)
    for user in users:
        if user.course_auto_push:
            # 等待1分钟，防止被tx冻结
            await asyncio.sleep(30)
            try:
                courses = await get_schedule(user.user_qq)
            except Exception as e:
                logger.error(f"获取课表失败，原因为{e}")
                continue
            res_msg = "今日课表如下:\n"
            today_courses = []
            week = await get_week()
            for course in courses:
                # 获取今天星期几
                today = datetime.datetime.now().weekday() + 1
                if course["weekDay"] == today:
                    # 判断本周是否有这节课
                    startWeek = course["startWeek"]
                    endWeek = course["endWeek"]
                    if startWeek <= week <= endWeek:
                        # 判断是否是单双周
                        if course["period"]:
                            if course["period"] == "单" and week % 2 == 0:
                                continue
                            elif course["period"] == "双" and week % 2 == 1:
                                continue
                        # 将课程信息添加到列表中
                        today_courses.append(course)
            # 按照课程开始时间排序
            today_courses.sort(key=lambda x: x["startSection"])
            for course in today_courses:
                res_msg += f"{course['courseName']}\n"
                res_msg += f"时间：第{course['startSection']}-{course['endSection']}节\n"
                res_msg += f"地点：{course['classRoom']}\n"
                res_msg += f"教师：{course['teacherName']}\n"
                res_msg += "----------------\n"
            await bot.send_private_msg(user_id=user.user_qq, message=res_msg + "加油，今天又是元气满满的一天！\n若要关闭课表推送，请发送“关闭课表推送”")
            # 20%概率触发语音
            if random.randint(1, 5) == 1:
                voice, voice_msg = await get_voice()
                await bot.send_private_msg(user_id=user.user_qq, message=voice_msg)
                await bot.send_private_msg(user_id=user.user_qq, message=voice)


async def get_schedule(user_qq):
    # 获取session
    sessionid, session_update_time = await HDU_Sign_User.get_session(user_qq)
    acc = await HDU_Sign_User.get_account(user_qq)
    pwd = await HDU_Sign_User.get_password(user_qq)
    if not sessionid:
        sessionid = await get_session(acc, pwd, user_qq)
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': sessionid,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL Build/RQ3A.210705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 AliApp(DingTalk/5.1.5) com.alibaba.android.rimet/13534898 Channel/212200 language/zh-CN UT4Aplus/0.2.25 colorScheme/light'
    }
    url = 'https://skl.hdu.edu.cn/api/course'
    data = {
        'startTime': '2022-10-24',
    }
    res = await AsyncHttpx.get(url=url, headers=headers, params=data)
    # 将res转换为json格式
    res = res.json()
    return res["list"]


async def get_week():
    # 获取当前周数
    # 2022-10-24是第九周
    start_time = datetime.datetime(2022, 10, 24)
    now_time = datetime.datetime.now()
    week = (now_time - start_time).days // 7 + 9
    return week


async def get_voice():
    voice = random.choice(os.listdir(RECORD_PATH / "chiya" / "course"))
    result = record(voice, "chiya/course")
    msg = voice.split(".")[0]
    return result, msg
