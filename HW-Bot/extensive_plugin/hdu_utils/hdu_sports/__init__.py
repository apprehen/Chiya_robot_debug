import re, json, datetime, asyncio
import nonebot
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.params import CommandArg
from nonebot import Driver
from utils.http_utils import AsyncHttpx
from utils.message_builder import custom_forward_msg
from services.log import logger
from .._models import HDU_Sign_User
from .data import *


driver: Driver = nonebot.get_driver()
# 插件信息
__zx_plugin_name__ = "阳光长跑"
__plugin_usage__ = """
usage：
    自动监听长跑数据变动
    在完成长跑后，推送当日长跑信息
    手动指令：
        我的长跑/今日长跑/上次长跑
    即可查看历史长跑信息
    首次使用请先使用（私聊！！！！）：
        set hdu 学号 密码（智慧杭电密码）
    绑定杭电通行证
    并私聊发送：
        set sports 密码
    绑定体联密码
""".strip()
__plugin_des__ = "阳光长跑信息查询与推送"
__plugin_cmd__ = ["我的长跑", "今日长跑", "上次长跑"]
__plugin_version__ = 0.4
__plugin_author__ = "Lycoiref"
__plugin_type__ = ("杭电生活", )
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["我的长跑", "今日长跑", "上次长跑"],
}


set_pwd = on_command("set sports", priority=5, block=True)
today_info = on_command("今日长跑", priority=5, block=True)
last_info = on_command("上次长跑", priority=5, block=True)
all_info = on_command("我的长跑", priority=5, block=True)


@set_pwd.handle()
async def _(bot: Bot, event: MessageEvent, arg: Message = CommandArg()):
    user_qq = event.user_id
    pwd = arg.extract_plain_text()
    if not pwd:
        await set_pwd.finish("请输入密码")
    await HDU_Sign_User.set_sports_password(user_qq, pwd)
    await set_pwd.finish("success")


@today_info.handle()
async def _(bot: Bot, event: MessageEvent):
    user_qq = event.user_id
    user = await HDU_Sign_User.get_user(user_qq)
    if not user:
        await today_info.finish("请先绑定杭电通行证")
    if not user.sports_password:
        await today_info.finish("请先绑定体联密码")
    try:
        res = await get_sports_info(user.hdu_account, user.sports_password)
    except TimeoutError:
        await today_info.finish("网络连接超时")
    except Exception as e:
        # 再试一次
        try:
            res = await get_sports_info(user.hdu_account, user.sports_password)
        except Exception as e:
            logger.error(e)
            await today_info.finish("获取失败，未知错误")
    last_run_data = res[-1]
    last_run_date = last_run_data['runnerTime'] # 格式为2021-04-01
    # 判断是否为当天
    # 获取当天日期
    today = datetime.date.today()
    if str(last_run_date) == str(today):
        # 匹配查看是否有效
        url = 'http://hdu.sunnysport.org.cn/runner/achievements.html'
        res_body = await AsyncHttpx.get(url, headers=headers)
        year = last_run_date.split('-')[0]
        month = last_run_date.split('-')[1]
        day = last_run_date.split('-')[2]
        pattern = f"{year}年{month}月{day}日.*(\\n.*){{6}}.*glyphicon glyphicon-ok"
        val = re.search(pattern, res_body.content.decode())
        if val:
            valid = "是否有效：✓"
        else:
            valid = "是否有效：✗"
        await today_info.finish(f"""你已经完成了今日长跑
配速为{round(last_run_data['runnerSpeed'], 2)}m/s
总距离为{last_run_data['runnerMileage']}米
{valid}""")
    else:
        await today_info.finish("未查询到今日的长跑信息")


@last_info.handle()
async def _(bot: Bot, event: MessageEvent):
    user_qq = event.user_id
    user = await HDU_Sign_User.get_user(user_qq)
    if not user:
        await last_info.finish("请先绑定杭电通行证")
    if not user.sports_password:
        await last_info.finish("请先绑定体联密码")
    try:
        res = await get_sports_info(user.hdu_account, user.sports_password)
    except TimeoutError:
        await last_info.finish("网络连接超时")
    except Exception as e:
        # 再试一次
        try:
            res = await get_sports_info(user.hdu_account, user.sports_password)
        except Exception as e:
            logger.error(e)
            await last_info.finish("获取失败，未知错误")
    last_run_data = res[-1]
    last_run_date = last_run_data['runnerTime'] # 格式为2021-04-01
    # 匹配查看是否有效
    url = 'http://hdu.sunnysport.org.cn/runner/achievements.html'
    res_body = await AsyncHttpx.get(url, headers=headers)
    year = last_run_date.split('-')[0]
    month = last_run_date.split('-')[1]
    day = last_run_date.split('-')[2]
    pattern = f"{year}年{month}月{day}日.*(\\n.*){{6}}.*glyphicon glyphicon-ok"
    val = re.search(pattern, res_body.content.decode())
    if val:
        valid = "是否有效：✓"
    else:
        valid = "是否有效：✗"
    await last_info.finish(f"""你上次完成长跑的时间为{last_run_date}
配速为{round(last_run_data['runnerSpeed'], 2)}m/s，总距离为{last_run_data['runnerMileage']}米
{valid}""")


@all_info.handle()
async def _(bot: Bot, event: MessageEvent):
    user_qq = event.user_id
    user = await HDU_Sign_User.get_user(user_qq)
    if not user:
        await all_info.finish("请先绑定杭电通行证")
    if not user.sports_password:
        await all_info.finish("请先绑定体联密码")
    try:
        res = await get_sports_info(user.hdu_account, user.sports_password)
    except TimeoutError:
        await all_info.finish("网络连接超时")
    except Exception as e:
        # 再试一次
        try:
            res = await get_sports_info(user.hdu_account, user.sports_password)
        except Exception as e:
            logger.error(e)
            await all_info.finish("获取失败，未知错误")
    # 计算平均跑步速度
    speed = 0
    for i in res:
        speed += i['runnerSpeed']
    speed = round(speed / len(res), 2)
    msg_list = [f"你的长跑信息如下：\n跑步次数：{len(res)}，平均配速：{speed}m/s"]
    msg = ""
    # 匹配查看是否有效
    url = 'http://hdu.sunnysport.org.cn/runner/achievements.html'
    res_body = await AsyncHttpx.get(url, headers=headers)
    # 每5条长跑信息发送一次
    for i in range(0, len(res), 5):
        for j in range(i, min(i+5, len(res))):
            msg += f"{res[j]['runnerTime']}\n配速为{round(res[j]['runnerSpeed'], 2)}m/s，总距离为{res[j]['runnerMileage']}米\n"
            year = res[j]['runnerTime'].split('-')[0]
            month = res[j]['runnerTime'].split('-')[1]
            day = res[j]['runnerTime'].split('-')[2]
            pattern = f"{year}年{month}月{day}日.*(\\n.*){{6}}.*glyphicon glyphicon-ok"
            val = re.search(pattern, res_body.content.decode())
            if val:
                msg += "是否有效：✓"
            else:
                msg += "是否有效：✗"
            if j != min(i+5, len(res))-1:
                msg += "\n\n"
        msg_list.append(msg)
        msg = ""
    # 检查是私聊还是群聊
    try:
        forward_msg_list = custom_forward_msg(msg_list, bot.self_id)
        await bot.send_group_forward_msg(group_id=event.group_id, messages=forward_msg_list)
    except:
        for msg in msg_list:
            await bot.send_private_msg(user_id=user_qq, message=msg)
            await asyncio.sleep(0.2)


async def get_sports_info(acc, pwd):
    url = 'http://hdu.sunnysport.org.cn/login/'
    session = AsyncHttpx()
    res = await session.get(url, headers=headers)
    cookie = res.headers['Set-Cookie'].split(';')[0]
    # print(res.content.decode())
    vrf = re.search('name="vrf" value="(.*?)">', res.content.decode()).group(1)
    data["username"] = acc
    data["password"] = pwd
    data["vrf"] = vrf
    # 将sessionid加入到headers中
    headers['Cookie'] = cookie
    url += '/login/'
    res = await session.post(url, data=data, headers=headers)
    cookie = res.headers['Set-Cookie'].split(';')[0]
    headers['Cookie'] = cookie
    data_url = 'http://hdu.sunnysport.org.cn/runner/data/speed.json'
    res = await session.get(data_url, headers=headers)
    print(res.text)
    return json.loads(res.text)
