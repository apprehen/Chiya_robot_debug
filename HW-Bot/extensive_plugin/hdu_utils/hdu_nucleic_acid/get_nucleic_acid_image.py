import requests
import time
import datetime
today = datetime.date.today()


info_url = 'https://api.metaspace.mjclouds.com/v1/info'
info_list = requests.get(info_url).json()['data']
lives = info_list['live']
live = lives[0]
print(live['ID'])

# 获取今天中午12:00的时间戳
today_12 = datetime.datetime(today.year, today.month, today.day, 12, 0, 0)
today_12_timestamp = int(time.mktime(today_12.timetuple()))
print(today_12_timestamp)

# 获取今天晚上18:00的时间戳
today_18 = datetime.datetime(today.year, today.month, today.day, 18, 0, 0)
today_18_timestamp = int(time.mktime(today_18.timetuple()))
print(today_18_timestamp)

data = {
    'EndTime': today_18_timestamp,
    'StartTime': today_12_timestamp,
    'LiveID': live['ID'],
    'NextStartTime': '',
}


res = requests.post('https://api.metaspace.mjclouds.com/v1/snap', json=data)
print(res.text)
