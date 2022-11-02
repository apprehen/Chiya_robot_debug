from urllib import parse
import requests
import re, json



if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.27',
    }
    data = {
        'username': '20011519',
        'password': 'Lyf20020911'
    }
    url = 'http://hdu.sunnysport.org.cn/login/'
    session = requests.Session()  # 保存会话
    res = session.get(url, headers=headers)
    cookie = res.headers['Set-Cookie'].split(';')[0]
    # print(res.content.decode())
    vrf = re.search('name="vrf" value="(.*?)">', res.content.decode()).group(1)
    data["vrf"] = vrf
    # data = parse.urlencode(data)
    # 输出所有cookie
    print(cookie)
    # sleep(5)
    # 将sessionid加入到headers中
    headers['Cookie'] = cookie
    print(data)
    url += '/login/'
    res = session.post(url, data=data, headers=headers, allow_redirects=False)
    cookie = res.headers['Set-Cookie'].split(';')[0]
    print(cookie)
    headers['Cookie'] = cookie
    data_url = 'http://hdu.sunnysport.org.cn/runner/data/speed.json'
    res = requests.get(data_url, headers=headers)
    run_data = res.text
    # 转为json格式
    res = json.loads(run_data)
    msg_list = ["你的长跑信息如下：\n"]
    msg = ""
    print(res)
    # 每5条长跑信息发送一次
    for i in range(0, len(res), 5):
        for j in range(i, min(i+5, len(res))):
            msg += f"{res[j]['runnerTime']} 配速为{round(res[j]['runnerSpeed'], 2)}m/s，总距离为{res[j]['runnerMileage']}米"
            # 匹配查看是否有效
            url = 'http://hdu.sunnysport.org.cn/runner/achievements.html'
            res_body = requests.get(url, headers=headers)
            # print(res_body.text)
            year = res[j]['runnerTime'].split('-')[0]
            month = res[j]['runnerTime'].split('-')[1]
            day = res[j]['runnerTime'].split('-')[2]
            pattern = f"{year}年{month}月{day}日.*(\\n.*){{6}}.*glyphicon glyphicon-ok"
            print(pattern)
            val = re.search(pattern, res_body.content.decode())
            if val:
                msg += "✓\n"
        msg_list.append(msg)
        msg = ""
    for msg in msg_list:
        print(msg)
        print("=============================================")
