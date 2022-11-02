from asyncio import sleep
import datetime
import os
import random
import sys
import time
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# 需要获取的信息
studentNumber = '20011511'  # 学号
cookie = ''
un = '20011519'
pd = 'Lyf20020911.'

# 静态数据
headers = {
    'Host': 'newjw.hdu.edu.cn',
    'Connection': 'keep-alive',
    'Origin': 'http://newjw.hdu.edu.cn',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Cookie': cookie,
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27'
}
gnmkdm = 'N253508'  # 功能模块代码

form = {
    'xnm': '2022',  # 学年
    'xqm': '1',  # 学期
    'kzlx': 'ck',  # 查询类型
    'xsdm': '',  # 学生代码
}

# 向http://newjw.hdu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html发送请求


def get_schedule():
    driver = webdriver.Chrome(service=Service(
        '/usr/bin/chromedriver'
    ), options=chrome_options)
    wait = WebDriverWait(driver, 3, 0.5)
    driver.get("http://newjw.hdu.edu.cn/sso/driot4login")
    wait.until(EC.presence_of_element_located((By.ID, "un")))
    wait.until(EC.presence_of_element_located((By.ID, "pd")))
    wait.until(EC.presence_of_element_located((By.ID, "index_login_btn")))
    driver.find_element(By.ID, 'un').clear()
    driver.find_element(By.ID, 'un').send_keys(un)  # 传送帐号
    driver.find_element(By.ID, 'pd').clear()
    driver.find_element(By.ID, 'pd').send_keys(pd)  # 输入密码
    driver.find_element(By.ID, 'index_login_btn').click()
    # wait.until(EC.presence_of_element_located((By.ID, "casLoginForm")))

    # driver.get('http://newjw.hdu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508&layout=default&su=20011511')
    cookies = driver.get_cookies()
    print(cookies)
    cookie = f'JSESSIONID={cookies[1]["value"]}; route={cookies[0]["value"]}'
    headers['Cookie'] = cookie
    print(cookie)
    r = requests.post(f'http://newjw.hdu.edu.cn/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm={gnmkdm}&su={studentNumber}', headers=headers, data=form)
    print(r.text)

get_schedule()
