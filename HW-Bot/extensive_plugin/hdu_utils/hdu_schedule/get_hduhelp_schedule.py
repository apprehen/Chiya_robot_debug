import datetime
import requests

sessionid = '7e3f884c-a52c-4460-a37a-37a9e691948e'
headers = {
    'Content-Type': 'application/json',
    'X-Auth-Token': sessionid,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL Build/RQ3A.210705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 AliApp(DingTalk/5.1.5) com.alibaba.android.rimet/13534898 Channel/212200 language/zh-CN UT4Aplus/0.2.25 colorScheme/light'
}
url = 'https://skl.hdu.edu.cn/api/course'
data = {
    'startTime': '2022-10-24',
}


def get_week():
    # 获取当前周数
    # 2022-10-24是第九周
    start_time = datetime.datetime(2022, 10, 24)
    now_time = datetime.datetime.now()
    week = (now_time - start_time).days // 7 + 9
    return week

if __name__ == '__main__':
    res = requests.get(url=url, headers=headers, params=data)
    # 将res.text转换为json格式
    res = res.json()
    list = res['list']
    for course in list:
        # 显示course的所有key
        # print(course.keys())
        # print(course)
        # if course["courseName"] == "大学物理实验B":
        #     print(course)
        # 获取今天星期几
        today = datetime.datetime.now().weekday() + 1
        if course["weekDay"] == today:
            startWeek = course['startWeek']
            endWeek = course['endWeek']
            week = get_week()
            print(week)
            if startWeek <= week <= endWeek:
                # 判断是否是单双周
                if course["period"]:
                    if course["period"] == "单" and week % 2 == 0:
                        continue
                    elif course["period"] == "双" and week % 2 == 1:
                        continue
                # 将课程信息添加到列表中
                print(course)
    print(datetime.datetime.now().weekday())
