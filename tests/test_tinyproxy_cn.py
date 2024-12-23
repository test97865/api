import requests

# Tinyproxy 代理服务器地址和端口
proxy = {
    "http": "http://42.193.120.78:8888",
    "https": "http://42.193.120.78:8888",
}

try:
    # 通过代理访问百度
    response = requests.get("http://www.baidu.com", proxies=proxy)

    # 打印响应内容
    print("Status Code:", response.status_code)
    print("Response Body:", response.text[:500])  # 打印前500个字符
except requests.exceptions.RequestException as e:
    print("Error:", e)