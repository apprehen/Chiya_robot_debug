import asyncio
import time
import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
try:
    from _models import HDU_Sign_User, db
except ImportError:
    from ._models import HDU_Sign_User, db

# selenium设置
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--proxy-server=http://172.16.16.165:8080')  # 使用代理

logging.basicConfig(filename='punch.log', encoding='utf-8', level=logging.DEBUG)


async def get_session(un, pd, user_qq):
    # 服务器端
    browser = webdriver.Chrome(service=Service(
        '/usr/bin/chromedriver'), chrome_options=chrome_options)
    # 本地
    browser = webdriver.Chrome(chrome_options=chrome_options)
    wait = WebDriverWait(browser, 3, 0.5)
    browser.get("http://httpbin.org/ip")
    if not 'pre' in browser.page_source:
        logging.error('代理出现错误')
    logging.info('开始获取session')
    try:
        browser.get("https://cas.hdu.edu.cn/cas/login")
        wait.until(EC.presence_of_element_located((By.ID, "un")))
        wait.until(EC.presence_of_element_located((By.ID, "pd")))
        wait.until(EC.presence_of_element_located((By.ID, "index_login_btn")))
        browser.find_element(By.ID, 'un').clear()
        browser.find_element(By.ID, 'un').send_keys(un)  # 传送帐号
        browser.find_element(By.ID, 'pd').clear()
        browser.find_element(By.ID, 'pd').send_keys(pd)  # 输入密码
        browser.find_element(By.ID, 'index_login_btn').click()
        # 检查是否为网络问题
    except TimeoutException:
        logging.error('请求/cas/login超时')
    except Exception as e:
        logging.error(e)
        logging.error('未知错误')

    try:
        wait.until(EC.presence_of_element_located((By.ID, "errormsg")))
        # message="打卡失败，请检查账号密码是否正确"， 可能需要使用bot发送消息
        logging.error(f"{user_qq}的账号密码错误")
        return
    except TimeoutException as e:
        browser.get("https://skl.hduhelp.com/passcard.html#/passcard")
        for retryCnt in range(10):
            time.sleep(1)
            sessionId = browser.execute_script(
                "return window.localStorage.getItem('sessionId')")
            if sessionId is not None and sessionId != '':
                break
        if sessionId is None or sessionId == '':
            logging.error('获取session失败')
        else:
            # 将获取的session存入数据库
            await HDU_Sign_User.set_session(user_qq, sessionId)
            print(f"{user_qq}的session为{sessionId},获取成功")
            return sessionId
    finally:
        browser.quit()


async def init_db():
    await db.set_bind('postgresql://chiya:chiya000@localhost:5432/chiya_db')
    await db.gino.create_all()


async def main():
    await init_db()
    users = await HDU_Sign_User.get_all_users(False)
    for user in users:
        user_qq = user.user_qq
        un = user.hdu_account
        pd = user.hdu_password
        logging.info(f"正在获取{user_qq}的session，学号为{un}")
        print(f"正在获取{user_qq}的session，学号为{un}")
        await get_session(un, pd, user_qq)
    # 执行完成后添加qq提醒，发送获取情况（几人成功，几人失败）


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # 设置定时任务
    scheduler = AsyncIOScheduler()
    scheduler.add_job(main, 'cron', hour=6, minute=1)
    scheduler.add_job(main, 'cron', hour=7, minute=0)
    scheduler.add_job(main, 'cron', hour=23, minute=0)
    scheduler.start()
    logging.info('已启动定时任务')
    print('已启动定时任务')
    asyncio.get_event_loop().run_forever()
