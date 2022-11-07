import requests
import ast
import asyncio
async def get_tianqi():
    city = "杭州"
    key ='22776ba380fd44ef9e85113bc869dbef'
    weapi= "https://devapi.qweather.com/v7/weather/3d?"
    idapi="https://geoapi.qweather.com/v2/city/lookup?"
    city= ast.literal_eval(requests.get(idapi+"key="+key+"&"+"location="+city).text)["location"][0]["id"]
    wea= ast.literal_eval(requests.get(weapi+"key="+key+"&"+"location="+city).text)
    todaywea= wea["daily"][0]["textDay"]
    tomwea = wea["daily"][1]["textDay"]
    weathertab = {
        "雨":"🌧",
        "雪":"❄",
        "晴":"☀",
        "云":"☁",
        "阴":"⛅"
    }
    todw="🌧"
    tomw="🌧"
    for i in weathertab:
        if i in todaywea:
            todw = weathertab[i]
        if i in tomwea:
            tomw = weathertab[i]

    return todw,tomw
timetab={
  "1":"🕗",
  "2":"🕘",
  "3":"🕙",
  "4":"🕚",
  "5":"🕝",
  "6":"🕞",
  "7":"🕟",
  "8":"🕠",
  "9":"🕢",
  "10":"🕣",
  "11":"🕘",
  "12":"🕤",
}
print(timetab['2'])