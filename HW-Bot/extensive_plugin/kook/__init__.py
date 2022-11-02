import nonebot
import json


from pydantic import BaseModel
from utils.utils import get_bot
from .config import *
from services.log import logger
from utils.http_utils import AsyncHttpx


class Verify(BaseModel):
    type: int
    channel_type: str
    challenge: str
    verify_token: str


class Item(BaseModel):
    s: int # 信令类型
    d: Union[Verify, None] = None # 信令数据


@app.get("/test")
async def custom_api():
    return {"message": "Hello, world!"}


@app.post("/kook/api")
async def _(request: Union[Item, Any]):
    bot = get_bot()
    try:
        logger.info(f"challenge: {request.d.challenge}")
        return {"challenge": request.d.challenge}
    except AttributeError:
        data = request["d"]
        if data['type'] == 9:
            nickname = data['extra']['author']['nickname']
            channel_name = data['extra']['channel_name']
            msg = data['content']
            await bot.send_group_msg(group_id=group_id, message=f"[{channel_name}]\n{nickname}:{msg}")
        elif data['type'] == 255:
            type = data['extra']['type']
            body = data['extra']['body']
            user_id = body['user_id']
            channel_id = body['channel_id']
            nickname = await get_nickname(user_id)
            channel_name = await get_channel_name(channel_id)
            if type == 'joined_channel':
                await bot.send_group_msg(group_id=group_id, message=f"[KOOK]:{nickname}加入{channel_name}频道语音")
            elif type == 'exited_channel':
                await bot.send_group_msg(group_id=group_id, message=f"[KOOK]:{nickname}退出{channel_name}频道语音")


async def get_nickname(user_id):
    url = f"{baseURL}/v3/user/view"
    params = {
        "user_id": user_id,
    }
    res = await AsyncHttpx().get(url, params=params, headers=http_headers)
    return json.loads(res.text)['data']['username']


async def get_channel_name(channel_id):
    url = f"{baseURL}/v3/channel/view"
    params = {
        "target_id": channel_id,
    }
    res = await AsyncHttpx().get(url, params=params, headers=http_headers)
    return json.loads(res.text)['data']['name']
