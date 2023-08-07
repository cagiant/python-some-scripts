import csv
import time
import random
from datetime import datetime, timedelta

def write_to_csv(file_path, timestamp, download_speed):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S'), f'{download_speed:.2f}' + "Kbps", f'{(download_speed/1024):.2f}' + "Mbps"])

def mock_download_speed(start_time):
    # 生成随机下载速度，范围在 0 Kbps 到 10000 Kbps 之间
    download_speed = random.uniform(0, 10000)
    write_to_csv('download_speed_cl.csv', start_time, download_speed)

# 设定日期为 2023-08-06
start_time = datetime(2023, 8, 6, 0, 0, 0)
end_time = start_time + timedelta(days=1)

# 每分钟生成一次随机数据并写入 CSV 文件，模拟一整天的数据
while start_time < end_time:
    start_time += timedelta(minutes=20)
    mock_download_speed(start_time)
    
