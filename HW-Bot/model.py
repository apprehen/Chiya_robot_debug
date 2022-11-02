from typing import Optional, Union, List
from datetime import datetime, timedelta
from gino import Gino

db = Gino()

class HDU_Sign_User(db.Model):
    __tablename__ = "hdu_auto_sign_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_qq = db.Column(db.BigInteger, nullable=False)
    hdu_account = db.Column(db.String(10))
    hdu_password = db.Column(db.String())
    auto_sign = db.Column(db.Boolean())
    hours = db.Column(db.Integer)
    minutes = db.Column(db.Integer)
    sessionid = db.Column(db.String()) # 用于保存登录后的sessionid，对应X-Auth-Token
    session_update_time = db.Column(db.DateTime)

    _idx1 = db.Index("hdu_punch_idx1", "user_qq", "hdu_account", unique=True)

    @classmethod
    async def add_account(cls, user_qq: int, hdu_account: str):
        """
        说明:
            添加一个hdu账号
        参数:
            :param user_qq： 用户qq
            :param hdu_account: 杭电账号
        """
        query = cls.query.where((cls.user_qq == user_qq) & (cls.hdu_account == hdu_account))
        user = await query.gino.first()
        if not user:
            await cls.create(
                user_qq=user_qq,
                hdu_account=hdu_account
            )
            return True
        return False

    @classmethod
    async def update_account(cls, user_qq: int, hdu_account: str):
        """
        说明:
            更新绑定的hdu账号
        参数:
            :param user_qq： 用户qq
            :param hdu_account: 杭电账号
        """
        query = cls.query.where((cls.user_qq == user_qq))
        user = await query.gino.first()
        if user:
            await user.update(
                hdu_account=hdu_account
            ).apply()
            return True
        return False

    @classmethod
    async def get_account(cls, user_qq: int):
        """
        说明:
            获取一个hdu账号
        参数:
            :param user_qq： 用户qq
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            return user.hdu_account
        return None

    @classmethod
    async def set_password(cls, user_qq: int, hdu_password: str):
        """
        说明:
            设置一个hdu账号的密码
        参数:
            :param user_qq： 用户qq
            :param hdu_password: 杭电密码
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            await user.update(hdu_password=hdu_password).apply()
            return True
        return False

    @classmethod
    async def get_password(cls, user_qq: int):
        """
        说明:
            查询一个hdu账号的密码
        参数:
            :param user_qq： 用户qq
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        return user.hdu_password

    @classmethod
    async def set_sign(cls, user_qq: int, auto_sign: bool):
        """
        说明:
            设置是否自动打卡
        参数:
            :param user_qq： 用户qq
            :param auto_sign: 是否自动打卡
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            await user.update(auto_sign=auto_sign).apply()
            return True
        return False

    @classmethod
    async def get_all_users(cls, auto: bool = True):
        """
        说明:
            获取所有用户
        """
        if auto:
            query = cls.query.where(cls.auto_sign == True)
        else:
            query = cls.query
        users = await query.gino.all()
        return users

    @classmethod
    async def get_time(cls, user_qq: int):
        """
        说明:
            获取用户打卡时间
        参数:
            :param user_qq： 用户qq
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        return user.hours, user.minutes

    @classmethod
    async def set_time(cls, user_qq: int, hour: int, minute: int):
        """
        说明:
            设置用户打卡时间
        参数:
            :param user_qq： 用户qq
            :param hour: 小时
            :param minute: 分钟
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            await user.update(hours=hour, minutes=minute).apply()
            return True
        return False

    @classmethod
    async def set_session(cls, user_qq: int, sessionid: str):
        """
        说明:
            设置用户session
        参数:
            :param user_qq： 用户qq
            :param sessionid: sessionid
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        if user:
            await user.update(sessionid=sessionid, session_update_time=datetime.now()).apply()
            return True
        return False

    @classmethod
    async def get_session(cls, user_qq: int):
        """
        说明:
            获取用户session
        参数:
            :param user_qq： 用户qq
        """
        query = cls.query.where(cls.user_qq == user_qq)
        user = await query.gino.first()
        return user.sessionid, user.session_update_time


async def init_db():
    await db.set_bind('postgresql://chiya:chiya000@localhost:5432/chiya_db')
    await db.gino.create_all()
