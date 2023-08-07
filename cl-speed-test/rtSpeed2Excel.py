import csv
import time
import hashlib
import base64
import hmac
import requests


password_hash='Hw08rVhc9TefbwK' # 浏览器获取
stok=']4tt0!70V30+0k0O[lY7f}it]rLc9xhr' # 初始值，不用管，后续会自动刷新

def get_rt_download_speed():
    if (is_login() == False):
        tp_login()
    return get_tp_data()


def is_login():
    response = do_get_tp_data()
    # 检查响应状态码
    return response.status_code == 200

def tp_login(max_retry=10):
    global stok
    url = "http://tplogin.cn/"
    data = {
        "method": "do",
        "login": {
            "password": password_hash
        }
    }
    response = requests.post(url, json=data)
    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功，响应内容：")
        print(response.json()['stok'])
        stok=response.json()['stok']
    else:
        print("请求失败，状态码：", response.status_code)
        tp_login(max_retry - 1)

def get_tp_data():
    response = do_get_tp_data()
    # 检查响应状态码
    if response.status_code == 200:
        # print("请求成功，响应内容：")
        # print(response.json())
        return calculate_speed(response.json())
    else:
        print("请求失败，状态码：", response.status_code)

def do_get_tp_data():
    url = "http://tplogin.cn/stok=" + stok + "/ds"
    data = {
        "hyfi": {
            "table": [
                "connected_ext"
            ]
        },
        "hosts_info": {
            "table": "online_host",
            "name": "cap_host_num"
        },
        "method": "get"
    }
    return requests.post(url, json=data)

def calculate_speed(data):
    online_hosts = data["hosts_info"]["online_host"]

    # 初始化 down_speed 总和
    total_down_speed = 0

    # 遍历每个元素并累加 down_speed 值
    for host_info in online_hosts:
        for host_key, host_data in host_info.items():
            down_speed = int(host_data["down_speed"])
            total_down_speed += down_speed
    total_down_speed_kb = (total_down_speed / 1024) * 8
    if total_down_speed_kb < 1:
        total_down_speed_kb = 0
    print("Total Down Speed:", total_down_speed_kb, "Kbs")
    return total_down_speed_kb

def write_to_csv(download_speed):
    with open('download_speed_cl.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), f'{download_speed:.2f}' + "Kbps", f'{(download_speed/1024):.2f}' + "Mbps"])

def send_to_feishu(download_speed):
    secret = 'fKoe4B1dLJjowpxh3q3vXc'
    timestamp = int(time.time())
    data = {
        "timestamp": str(timestamp),
        "sign": gen_sign(timestamp, secret),
        "msg_type": "text",
        "content": {
            "text": f"当前宽带下行峰值：{download_speed:.2f} Mbps"
        }
    }
    url = "https://open.feishu.cn/open-apis/bot/v2/hook/ece3947a-dee9-4ab1-879b-beddb0bae4a5"
    # 发送POST请求
    response = requests.post(url, json=data)
    # 检查响应状态码
    if response.status_code == 200:
        print("飞书群发送成功")
    else:
        print("请求失败，状态码：", response.status_code)

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign

if __name__ == "__main__":
    while True:
        print("开始测试，时间 " + time.strftime('%Y-%m-%d %H:%M:%S'))
        download_speed = get_rt_download_speed()
        print(f"当前宽带下行峰值：{download_speed:.2f} Kbps")
        write_to_csv(download_speed)
        send_to_feishu(download_speed)
        time.sleep(10)  # 等待 20 分钟（20 * 60 秒）
