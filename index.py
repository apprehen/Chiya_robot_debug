import requests
import ast
import asyncio
async def get_tianqi():
    city = "ζ­ε·"
    key ='22776ba380fd44ef9e85113bc869dbef'
    weapi= "https://devapi.qweather.com/v7/weather/3d?"
    idapi="https://geoapi.qweather.com/v2/city/lookup?"
    city= ast.literal_eval(requests.get(idapi+"key="+key+"&"+"location="+city).text)["location"][0]["id"]
    wea= ast.literal_eval(requests.get(weapi+"key="+key+"&"+"location="+city).text)
    todaywea= wea["daily"][0]["textDay"]
    tomwea = wea["daily"][1]["textDay"]
    weathertab = {
        "ι¨":"π§",
        "ιͺ":"β",
        "ζ΄":"β",
        "δΊ":"β",
        "ι΄":"β"
    }
    todw="π§"
    tomw="π§"
    for i in weathertab:
        if i in todaywea:
            todw = weathertab[i]
        if i in tomwea:
            tomw = weathertab[i]

    return todw,tomw
timetab={
  "1":"π",
  "2":"π",
  "3":"π",
  "4":"π",
  "5":"π",
  "6":"π",
  "7":"π",
  "8":"π ",
  "9":"π’",
  "10":"π£",
  "11":"π",
  "12":"π€",
}
print(timetab['2'])