import requests
import random
from datetime import datetime
import json

# 加载配置文件
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 随机生成颜色
def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))  # 生成随机颜色代码

# 定义表情符号类别和对应的表情，现版微信测试公众号本无法使用随机字体颜色和随机emoj表情
emoji = {
    "greeting": ["🎉", "🎈", "🎁"],  # 问候表情
    "date": ["📅", "📆"],  # 日期表情
    "love_days": ["❤️", "💖", "💕"],  # 相恋天数表情
    "weather": ["☀️", "🌧️", "⛅", "❄️", "🌪️"],  # 天气表情
    "temp": ["🌡️", "🌡️"],  # 气温表情
    "birthday": ["🎂", "🎉", "🎁"],  # 生日表情
    "anniversary": ["💍", "👰", "🤵"],  # 结婚纪念日表情
    "advice": ["🧥", "🧣", "🧤"],  # 天气提示表情
    "quote": ["💌", "😘", "😍"],  # 情话表情
    "remark": ["😊", "🤗", "🥰"]  # 结尾祝福表情
}

# 随机选择表情
def get_random_emoji(category):
    return random.choice(emoji.get(category, []))

# 获取和风天气的实时天气
def get_weather(location, api_key):
    url = f"https://devapi.qweather.com/v7/weather/now?location={location}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = data["now"]
        return weather
    except Exception as e:
        print(f"获取天气失败：{e}")
        return {"text": "未知", "temp": "未知"}

# 根据天气情况生成提示
def get_weather_advice(weather_text, temperature):
    umbrella_advice = ""  # 雨雪提醒
    clothing_advice = ""  # 穿衣建议

    if "雨" in weather_text or "雪" in weather_text:
        umbrella_advice = "记得带伞"

    temp = int(temperature)
    if temp <= 10:
        clothing_advice = "天气冷，记得穿上厚外套或羽绒服"
    elif temp <= 20:
        clothing_advice = "温度适中，可以穿薄外套或夹克"
    else:
        clothing_advice = "天气较热，可以穿短袖或T恤"

    return umbrella_advice, clothing_advice

# 计算距离目标日期的天数
def calculate_days(birthday_str):
    today = datetime.now()
    birthday = datetime.strptime(birthday_str, "%Y-%m-%d")

    # 如果生日在今天之前，计算到明年的生日
    if (birthday.month, birthday.day) < (today.month, today.day):
        next_birthday = datetime(today.year + 1, birthday.month, birthday.day)
    else:
        next_birthday = datetime(today.year, birthday.month, birthday.day)

    # 计算天数差
    delta = next_birthday - today
    return delta.days

# 获取每日情话
def get_love_quote():
    try:
        response = requests.get(config["loveQuotes"]["api"], timeout=5)  # 设置超时时间
        response.raise_for_status()
        data = response.json()
        if "returnObj" in data and isinstance(data["returnObj"], list) and data["returnObj"]:
            return data["returnObj"][0]  # 返回 API 提供的第一条情话
        else:
            print("情话 API 返回的数据格式不正确，使用默认情话。")
            return random.choice(config["loveQuotes"]["fallback"])
    except requests.exceptions.RequestException as e:
        print(f"获取情话失败：{e}，使用默认情话。")
        return random.choice(config["loveQuotes"]["fallback"])

# 构造消息内容
def create_message():
    # 获取天气信息
    weather_info = get_weather(config["location"], config["heFengAPIKey"])
    if not weather_info or "text" not in weather_info or "temp" not in weather_info:
        weather_info = {"text": "未知", "temp": "未知"}  # 默认值

    # 计算相恋天数
    start_date = datetime.strptime(config["importantDates"]["startDate"], "%Y-%m-%d")
    love_days = (datetime.now() - start_date).days

    # 获取生日信息
    person1 = config["importantDates"]["birthdays"]["person1"]
    person2 = config["importantDates"]["birthdays"]["person2"]
    birthday1 = calculate_days(person1["birthday"])
    birthday2 = calculate_days(person2["birthday"])
    wedding_days = calculate_days(config["importantDates"]["weddingAnniversary"])

    # 获取情话
    love_quote = get_love_quote()

    # 获取天气提示
    umbrella_advice, clothing_advice = get_weather_advice(weather_info["text"], weather_info["temp"])

    # 构造消息内容（直接生成字典格式）
    message_data = {
        "first": {"value": f"今天的温馨提醒来啦！{get_random_emoji('greeting')}", "color": get_random_color()},
        "keyword1": {"value": f"{datetime.now().strftime('%Y年%m月%d日')}{get_random_emoji('date')}", "color": get_random_color()},
        "keyword2": {"value": f"{love_days}天{get_random_emoji('love_days')}", "color": get_random_color()},
        "keyword3": {"value": f"{weather_info['text']}{get_random_emoji('weather')}", "color": get_random_color()},
        "keyword4": {"value": f"{weather_info['temp']}°C{get_random_emoji('temp')}", "color": get_random_color()},
        "person1": {"value": f"{person1['name']}{get_random_emoji('birthday')}", "color": get_random_color()},
        "keyword5": {"value": f"{birthday1}天{get_random_emoji('birthday')}", "color": get_random_color()},
        "person2": {"value": f"{person2['name']}{get_random_emoji('birthday')}", "color": get_random_color()},
        "keyword6": {"value": f"{birthday2}天{get_random_emoji('birthday')}", "color": get_random_color()},
        "keyword7": {"value": f"{wedding_days}天{get_random_emoji('anniversary')}", "color": get_random_color()},
        "keyword8": {"value": f"{umbrella_advice} {clothing_advice}{get_random_emoji('advice')}", "color": get_random_color()},
        "keyword9": {"value": f"{love_quote}{get_random_emoji('quote')}", "color": get_random_color()},
        "remark": {"value": f"祝你开心每一天！{get_random_emoji('remark')}", "color": get_random_color()}
    }
    return message_data

# 获取 Access Token
def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={config['appID']}&secret={config['appSecret']}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"获取 Access Token 失败：{e}")
        return None

# 推送消息
def send_message():
    access_token = get_access_token()
    if not access_token:
        print("获取 Access Token 失败")
        return

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    message_data = create_message()  # 获取消息数据

    for user in config["user"]:
        message = {
            "touser": user,
            "template_id": config["templateID"],
            "data": message_data
        }
        try:
            response = requests.post(url, json=message)
            print(response.json())
        except Exception as e:
            print(f"消息发送失败：{e}")

if __name__ == "__main__":
    send_message()
