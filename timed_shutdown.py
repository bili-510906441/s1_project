import datetime
import subprocess
import sys

if sys.platform != 'win32':
    raise NotImplementedError('不支持此系统。')

version = '1.0'
print('定时关机小程序 v' + version)

def calculate_shutdown_time():
    hour_str = input('小时: ')
    minute_str = input('分钟: ')
    current_time = datetime.datetime.now()
    try:
        hour_int = int(hour_str)
        minute_int = int(minute_str)
        current_time_hour = int(current_time.hour)
        current_time_minute = int(current_time.minute)
        next_day = True if hour_int < current_time_hour or (hour_int == current_time_hour and minute_int <= current_time_minute) else False
    except ValueError:
        print('无效的时间格式。按“Enter”关闭程序。')
        sys.exit(0)
    try:
        input_time = datetime.datetime(current_time.year, current_time.month, current_time.day + 1 if next_day else current_time.day, hour_int, minute_int, 0)
    except ValueError:
        input_time = datetime.datetime(current_time.year, current_time.month + 1, 1, hour_int, minute_int, 0)
    delta = str((input_time - current_time).seconds)
    print('当前时间： ' + str(current_time.strftime('%Y-%m-%d %H:%M:%S')))
    print('定时关机时间： ' + str(input_time))
    print('运行命令： shutdown -s -f -t ' + delta)
    subprocess.Popen('shutdown -s -f -t ' + delta)

if __name__ == "__main__":
    calculate_shutdown_time()
