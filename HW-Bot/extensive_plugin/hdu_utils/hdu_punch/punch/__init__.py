import random
import datetime
import time


import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot import Driver
from utils.http_utils import AsyncHttpx
from utils.utils import scheduler, get_bot
from services.log import logger
from ..._models import HDU_Sign_User
from ...get_session import get_session


driver: Driver = nonebot.get_driver()
# 插件信息
__zx_plugin_name__ = "杭电健康打卡"
__plugin_usage__ = """
usage：
    杭电自动健康打卡
    私聊发送指令：
    $0$2$14-hw-Lycoiref
    注意：本程序旨在提供更为便利的打卡方式，
    请确保打卡信息准确，遵守防疫规定
    若因填写虚假信息造成后果的
    本程序不承担任何责任
""".strip()
__plugin_des__ = "punchhdu"
__plugin_cmd__ = ["打开杭电自动健康打卡/关闭杭电自动健康打卡"]
__plugin_version__ = 1.0
__plugin_author__ = "Lycoiref"
__plugin_type__ = ("杭电生活", )
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["punchhdu"],
}

open_auto_punch = on_command("openpunch", priority=5, block=True)
close_auto_punch = on_command("closepunch", priority=5, block=True)
punch_now = on_command("punchin", priority=5, block=True)
# 绑定杭电通行证
bind = on_command("set punch", aliases={"set hdu"}, priority=5, block=True)
auth_code = on_command("$0$2$14-hw-Lycoiref", priority=5, block=True)


@punch_now.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        user_qq = event.user_id
        account = await HDU_Sign_User.get_account(user_qq)
        if account:
            password = await HDU_Sign_User.get_password(user_qq)
            await auto_punch(event.user_id, account, password)
        else:
            await punch_now.finish("请先绑定杭电通行证")
    except Exception as e:
        logger.error(e)
        await punch_now.finish("打卡失败，请稍后重试")


@open_auto_punch.handle()
async def _(bot: Bot, event: MessageEvent):
    acc = await HDU_Sign_User.get_account(event.user_id)
    pwd = await HDU_Sign_User.get_password(event.user_id)
    if acc:
        await HDU_Sign_User.set_sign(event.user_id, True)
        # 随机生成打卡时间（小时和分钟）
        hour = random.randint(6, 23)
        minute = random.randint(0, 59)
        # 存入数据库
        save_time = await HDU_Sign_User.set_time(event.user_id, hour, minute)
        if not save_time:
            await open_auto_punch.finish("打卡时间设置失败，请稍后重试")
        try:
            scheduler.add_job(
                func=auto_punch,
                trigger="cron",
                hour=hour,
                minute=minute,
                second=0,
                misfire_grace_time=60,
                id=f"auto_punch_{event.user_id}",
                args=[event.user_id, acc, pwd],
            )
        except Exception as e:
            logger.error(e)
            await open_auto_punch.finish("已经开启过了，请勿重复开启")
        await open_auto_punch.finish(f"已开启hdu_punch，你的打卡时间为每天{hour}点{minute}分")
    else:
        await open_auto_punch.finish("请先绑定hdu通行证")


@close_auto_punch.handle()
async def _(bot: Bot, event: MessageEvent):
    try:
        # 删除定时任务
        scheduler.remove_job(f"auto_punch_{event.user_id}")
        await HDU_Sign_User.set_sign(event.user_id, False)
    except Exception as e:
        logger.error(e)
        await close_auto_punch.finish("尚未开启hdu_punch")
    await close_auto_punch.finish("已关闭hdu_punch")


@bind.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    message = arg.extract_plain_text()
    if message:
        acc, pwd = message.split()
        # 查询是否已经绑定
        if await HDU_Sign_User.get_account(event.user_id):
            acc_s = await HDU_Sign_User.update_account(event.user_id, acc)
        else:
            acc_s = await HDU_Sign_User.add_account(event.user_id, acc)
        pwd_s = await HDU_Sign_User.set_password(event.user_id, pwd)
        if not await HDU_Sign_User.get_sports_password(event.user_id):
            # 默认体联账号为学号
            await HDU_Sign_User.set_sports_password(event.user_id, acc)
        # 获取session
        await get_session(acc, pwd, event.user_id)
        if acc_s and pwd_s:
            await bind.finish("绑定成功")
        else:
            await bind.finish("绑定失败")


@auth_code.handle()
async def _(bot: Bot, event: MessageEvent):
    await auth_code.finish("""绑定指令: 
set punch 账号 密码
set hdu 账号 密码
栗子：set hdu 22017777 123456
打开自动打卡指令：
openpunch
关闭自动打卡指令：
closepunch
手动打卡指令：
punchin""")


# 设置定时任务
@driver.on_bot_connect
async def _():
    user_list = await HDU_Sign_User.get_all_users()
    for user in user_list:
        logger.info(user.auto_sign)
        hour, minute = await HDU_Sign_User.get_time(user.user_qq)
        if not hour or not minute:
            # 随机生成打卡时间（小时和分钟）
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)
            # 存入数据库
            save_time = await HDU_Sign_User.set_time(user.user_qq, hour, minute)
            if not save_time:
                logger.error("打卡时间设置失败")
        if user.auto_sign:
            scheduler.add_job(
                func=auto_punch,
                trigger="cron",
                hour=hour,
                minute=minute,
                second=0,
                misfire_grace_time=60,
                id=f"auto_punch_{user.user_qq}",
                args=[user.user_qq, user.hdu_account, user.hdu_password],
            )
            logger.info(
                f"hdu_auto_punch add_job：USER：{user.user_qq} acc：{user.hdu_account} " f"杭电健康打卡定时任务已开启"
            )


async def punch(bot, user_id, acc, pwd, retry):
    # 获取sessionid
    sessionid, session_time = await HDU_Sign_User.get_session(user_id)
    # 判断sessionid是否在三天内
    if sessionid and session_time:
        # session_time的格式为：2022-10-21 05:03:54.101276+00:00
        # 将session_time转换为时间戳
        session_time = int(time.mktime(time.strptime(str(session_time), "%Y-%m-%d %H:%M:%S.%f+00:00")))
        print(session_time)
        # 获取当前时间戳
        now_time = int(time.time())
        # 判断sessionid是否在三天内
        if now_time - session_time < 259200:
            # 在三天内
            logger.info(f"sessionid在三天内，无需重新获取")
        else:
            # 不在三天内
            logger.info(f"sessionid不在三天内，重新获取")
            bot.send_private_msg(
                user_id=user_id,
                message="sessionid已过期",
            )
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': sessionid,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL Build/RQ3A.210705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 AliApp(DingTalk/5.1.5) com.alibaba.android.rimet/13534898 Channel/212200 language/zh-CN UT4Aplus/0.2.25 colorScheme/light'
    }
    url = "https://skl.hdu.edu.cn/api/punch"
    data = {
        "currentLocation": "浙江省杭州市钱塘区",
        "city": "杭州市",
        "districtAdcode": "330114",
        "province": "浙江省",
        "district": "钱塘区",
        "healthCode": 0,
        "healthReport": 0,
        "currentLiving": 0,
        "last14days": 0
    }
    # un = os.environ["SCHOOL_ID"].strip()  # 学号
    # pd = os.environ["PASSWORD"].strip()  # 密码
    un = acc
    pd = pwd
    logger.info(f"正在打卡，账号：{un}")
    for retryCnt in range(3):
        try:
            logger.info(headers)
            res = await AsyncHttpx.post(url, json=data, headers=headers, timeout=30)
            logger.info(f"打卡结果：{res}")
            if res.status_code == 200:
                await bot.send_private_msg(
                    user_id=user_id,
                    message="hdupunch success",
                )
                return "hdupunch success"
            elif res.status_code == 401:
                logger.info(f"打卡失败，账号：{un}，原因：sessionid过期")
                # 获取sessionid
                sessionid = await get_session(acc, pwd, user_id)
                if sessionid:
                    # 重新打卡
                    await punch(bot, user_id, acc, pwd, retry)
                    return
                else:
                    logger.info(f"获取sessionid失败")
                    await bot.send_private_msg(
                        user_id=user_id,
                        message="获取sessionid失败，请检查账号密码是否正确。若账号密码正确，可能是网络问题，请联系管理员",
                    )
            elif retryCnt == 3:
                logger.error(f"打卡失败，错误码：{res.status_code}")
                bot.send_private_msg(
                    user_id=user_id, message=f"打卡失败，错误码：{res.status_code}")
        except Exception as e:
            logger.error(e)
            if retryCnt < 2:
                print(e.__class__.__name__ + "打卡失败，正在重试")
                time.sleep(3)
            else:
                await bot.send_private_msg(user_id=user_id, message="打卡失败，请联系管理员")


async def auto_punch(user_qq, acc, pwd, retry=False):
    try:
        bot = get_bot()
        await punch(bot, user_qq, acc, pwd, retry)
        # await bot.send_private_msg(user_id=user_qq, message=return_data)
    except Exception as e:
        logger.error(e)
        await bot.send_private_msg(user_id=user_qq, message="打卡失败，请稍后重试")
