import os
import random
import time

import requests


def generate_trace_id():
    current_timestamp = int(time.time() * 1000)
    binary_timestamp = bin(current_timestamp)[2:]
    random_number = random.randint(0, 8388607)
    binary_random_number = bin(random_number)[2:]
    concatenated_binary = binary_timestamp + binary_random_number
    return hex(int(concatenated_binary))[2:]

def send_trace_id(url, trace_id, trace_desc):
    # 设置请求头
    # headers = {
    #     "Content-Type": "application/json",
    #     "x-sky-sign": md5_signature,
    #     "x-sky-time": timestamp,
    #     "x-sky-id": "12334566",
    #     "x-sky-appid": appid,
    #     "x-sky-user": user
    # }
    current_timestam = int(time.time())
    params = {
        'traceIds': trace_id,
        'desc': f"{os.getenv('env_name')}环境：{trace_desc}",
        'time': current_timestam
    }
    response = requests.get(url, params=params)
    return response

if __name__ == "__main__":
    print(generate_trace_id())