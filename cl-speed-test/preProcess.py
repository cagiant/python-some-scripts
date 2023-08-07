import csv
import datetime
import re

DATA_DIR = "data/"
TIME_FORMAT = "%Y-%m-%d %H:%M"
THE_DATE = "2023-08-04"


def get_file_list(name):
    name_and_file_dic = {
        "唐其彪": ["download_speed_0805_唐其彪.csv", "download_speed_0807_唐其彪.csv"],
        "陈玲": ["download_speed_cl.csv"],
        "童烨彬": ["download_speed-0805-tyb.csv", "download_speed-0806-tyb.csv", "download_speed_tyb.csv"]
    }
    return name_and_file_dic.get(name, [])


def get_data(file_name_list):
    data = []
    for file_name_tmp in file_name_list:
        with open(DATA_DIR + file_name_tmp, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
    return data


def get_user_data(name_list):
    data_dic_tmp = {}
    for name in name_list:
        file_list = get_file_list(name)
        data_dic_tmp[name] = get_data(file_list)
    return data_dic_tmp


def retrieve_data(data, current_time):
    #  data format: [time, value1, value2]
    #  Find the value closest to current_time within the next 20 minutes,
    #  return value2 without "Mbps", or 0 if not found
    nearest_time_diff = float('inf')
    nearest_value = None

    for entry in data:
        entry_time = datetime.datetime.strptime(entry[0], TIME_FORMAT + ":%S")
        time_diff = abs((current_time - entry_time).total_seconds())

        if 0 <= time_diff < 1200:  # Check within the next 20 minutes
            if time_diff < nearest_time_diff:
                nearest_time_diff = time_diff
                nearest_value = entry[2]

    return float(re.sub(r'Mbps', '', nearest_value)) if nearest_value else 0

if __name__ == "__main__":
    # 生成时间列表，从00:00到23:40，以20分钟为间隔
    start_time = datetime.datetime.strptime(THE_DATE + " 00:00", "%Y-%m-%d %H:%M")
    end_time = datetime.datetime.strptime(THE_DATE + " 23:40", "%Y-%m-%d %H:%M")
    name_list = ['唐其彪', '陈玲', '童烨彬']
    data_dic = get_user_data(name_list)

    time_interval = datetime.timedelta(minutes=20)

    name_time_dic = {}
    time_list = ['用户']

    current_time = start_time
    while current_time <= end_time:
        for name in name_list:
            if name not in name_time_dic:
                name_time_dic[name] = {}
            name_time_dic[name][current_time] = retrieve_data(data_dic[name], current_time)
        time_list.append(current_time.strftime("%H:%M"))
        current_time += time_interval

    data_list = []
    for name in name_list:
        current_time = start_time
        data_tmp = [name]
        while current_time <= end_time:
            data_tmp.append(name_time_dic[name][current_time])
            current_time += time_interval
        data_list.append(data_tmp)

    # 写入CSV文件
    file_name = start_time.strftime("%Y-%m-%d") + ".csv"
    with open(file_name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(time_list)
        writer.writerows(data_list)
