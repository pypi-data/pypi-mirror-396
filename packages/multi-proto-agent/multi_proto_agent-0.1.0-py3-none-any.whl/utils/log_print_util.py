from datetime import datetime

def log_print(text):
    current_time = datetime.now()
    # 格式化时间为 yyyy-MM-dd HH:mm:SS
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{formatted_time}]{text}")