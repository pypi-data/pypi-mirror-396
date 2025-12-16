import psutil
import time
import argparse
import os
import json
from datetime import datetime
from spirems.msg_helper import QoS, Rate
from spirems.msg_helper import get_all_msg_types, get_all_msg_schemas, get_all_foxglove_schemas, load_msg_types, def_msg
from spirems.publisher import Publisher


# 上次的硬盘IO统计，用于计算每秒写入量
previous_disk_io = psutil.disk_io_counters()
previous_net_io = psutil.net_io_counters()

# 用于保存每个进程上次的写入量，用于计算每秒写入量
previous_process_io_write = {}
previous_process_io_read = {}


def get_system_cpu_usage():
    sensors_temperatures = psutil.sensors_temperatures()
    if 'coretemp' in sensors_temperatures:
        cpu_temp = sensors_temperatures['coretemp'][0].current
    elif 'k10temp' in sensors_temperatures:
        cpu_temp = sensors_temperatures['k10temp'][0].current
    else:
        cpu_temp = 0.0
    return psutil.cpu_percent(interval=0.1), cpu_temp

def get_system_memory_usage():
    mem = psutil.virtual_memory()
    return {
        'total': mem.total / (1024 ** 3),  # GB
        'used': mem.used / (1024 ** 3),    # GB
        'available': mem.available / (1024 ** 3),  # GB
        'percent': mem.percent  # 内存占用百分比
    }

def get_system_disk_write_usage():
    global previous_disk_io
    
    # 获取当前硬盘IO
    current_disk_io = psutil.disk_io_counters()
    
    # 计算当前秒的硬盘写入量
    write_bytes = (current_disk_io.write_bytes - previous_disk_io.write_bytes) / (1024 ** 2)  # MB
    read_bytes = (current_disk_io.read_bytes - previous_disk_io.read_bytes) / (1024 ** 2)  # MB
    previous_disk_io = current_disk_io  # 更新上次的硬盘IO统计
    
    return write_bytes, read_bytes  # MB

def get_system_network_usage():
    global previous_net_io

    net_io = psutil.net_io_counters()
    bytes_sent = (net_io.bytes_sent - previous_net_io.bytes_sent) / (1024 ** 2)  # MB
    bytes_recv = (net_io.bytes_recv - previous_net_io.bytes_recv) / (1024 ** 2)  # MB
    previous_net_io = net_io
    return bytes_sent, bytes_recv  # MB

def get_process_cpu_usage():
    process_info = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu_usage = proc.info['cpu_percent']

            # 获取进程的完整命令行（列表形式）
            cmd_list = proc.cmdline()
            # 拼接为字符串（类似htop的COMMAND显示）
            cmd_str = ' '.join(cmd_list) if cmd_list else proc.name()  # 若cmdline为空，用进程名替代
            
            process_info.append({
                'pid': pid,
                'name': cmd_str,
                'cpu_usage': cpu_usage
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return process_info

def get_process_memory_usage():
    process_info = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            mem_usage = proc.info['memory_info'].rss / (1024 ** 2)  # MB

            # 获取进程的完整命令行（列表形式）
            cmd_list = proc.cmdline()
            # 拼接为字符串（类似htop的COMMAND显示）
            cmd_str = ' '.join(cmd_list) if cmd_list else proc.name()  # 若cmdline为空，用进程名替代

            process_info.append({
                'pid': pid,
                'name': cmd_str,
                'mem_usage': mem_usage
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return process_info

def get_process_disk_write_usage():
    process_info = []
    for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            io_counters = proc.info['io_counters']
            
            if io_counters:  # 检查 io_counters 是否有效
                # 获取上一次记录的写入量
                previous_write_bytes = previous_process_io_write.get(pid, io_counters.write_bytes)
                previous_read_bytes = previous_process_io_read.get(pid, io_counters.read_bytes)
                
                # 计算当前秒的硬盘写入量（字节差值）
                write_bytes = (io_counters.write_bytes - previous_write_bytes) / (1024 ** 2)  # MB
                read_bytes = (io_counters.read_bytes - previous_read_bytes) / (1024 ** 2)  # MB
                
                # 更新上次的硬盘写入量
                previous_process_io_write[pid] = io_counters.write_bytes
                previous_process_io_read[pid] = io_counters.read_bytes

                # 获取进程的完整命令行（列表形式）
                cmd_list = proc.cmdline()
                # 拼接为字符串（类似htop的COMMAND显示）
                cmd_str = ' '.join(cmd_list) if cmd_list else proc.name()  # 若cmdline为空，用进程名替代
                
                process_info.append({
                    'pid': pid,
                    'name': cmd_str,
                    'write_bytes': write_bytes,
                    'read_bytes': read_bytes
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return process_info

def print_top_processes_by_cpu(process_info):
    sorted_by_cpu = sorted(process_info, key=lambda x: x['cpu_usage'], reverse=True)
    print("\nTop 10 processes by CPU usage:")
    info = []
    for idx, proc in enumerate(sorted_by_cpu[:10], 1):
        s = f"{idx}. CPU Usage: {proc['cpu_usage']:.2f}%, Name: {proc['name']}, PID: {proc['pid']}"
        print(s)
        info.append(s)
    return info

def print_top_processes_by_memory(process_info):
    sorted_by_memory = sorted(process_info, key=lambda x: x['mem_usage'], reverse=True)
    print("\nTop 10 processes by memory usage:")
    info = []
    for idx, proc in enumerate(sorted_by_memory[:10], 1):
        s = f"{idx}. Memory Usage: {proc['mem_usage']:.2f} MB, Name: {proc['name']}, PID: {proc['pid']}"
        print(s)
        info.append(s)
    return info

def print_top_processes_by_disk_write(process_info):
    sorted_by_disk_write = sorted(process_info, key=lambda x: x['write_bytes'], reverse=True)
    print("\nTop 10 processes by IO write/read usage:")
    info = []
    for idx, proc in enumerate(sorted_by_disk_write[:10], 1):
        s = f"{idx}. IO Write/Recv: {proc['write_bytes']:.2f} MB/s, IO Read/Sent: {proc['read_bytes']:.2f} MB/s, Name: {proc['name']}, PID: {proc['pid']}"
        print(s)
        info.append(s)
    return info


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--save-path',
        type=str,
        default='',
        help='mcap文件的保存路径.')
    parser.add_argument(
        '--ip',
        type=str,
        default='127.0.0.1',
        help='SpireMS Core IP.')
    parser.add_argument(
        '--port',
        type=int,
        default=9094,
        help='SpireMS Core Port.')
    parser.add_argument(
        '--tomcap',
        action='store_true',
        help='是否保存mcap文件.'
    )
    args = parser.parse_args()

    r = Rate(1)

    if args.tomcap:
        from mcap.writer import Writer
        now = datetime.now()
        mcap_f = open(os.path.join(args.save_path, now.strftime("smstop_%Y-%m-%d_%H-%M-%S.mcap")), "wb")
        writer = Writer(mcap_f)
        writer.start()
        schema_id = writer.register_schema(
            name="std_msgs::SystemStatus",
            encoding="jsonschema",
            data=json.dumps(
                {
                    "type": "object",
                    "properties": {},
                }
            ).encode(),
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic="/system/status",
            message_encoding="json",
        )

    pub = Publisher('/system/status', 'std_msgs::SystemStatus', ip=args.ip, port=args.port)
    msg = def_msg("std_msgs::SystemStatus")
    while True:
        try:
            # 获取当前系统的CPU占用率
            system_cpu_usage, cpu_temp = get_system_cpu_usage()
            msg["cpu_usage"] = system_cpu_usage
            msg["cpu_temp"] = cpu_temp
            
            # 获取当前系统的内存占用情况
            system_memory = get_system_memory_usage()
            msg["mem_usage"] = system_memory['percent']
            
            disk_free = psutil.disk_usage('/').free / (1024 ** 3)  # GB
            msg["disk_free"] = disk_free

            # 获取当前系统的硬盘写入量
            system_disk_write, system_disk_read = get_system_disk_write_usage()
            msg["disk_write"] = system_disk_write
            msg["disk_read"] = system_disk_read

            # 获取当前系统的网络收发情况
            system_net_sent, system_net_recv = get_system_network_usage()
            msg["net_sent"] = system_net_sent
            msg["net_recv"] = system_net_recv
            
            # 获取当前进程的CPU占用率
            process_info_cpu = get_process_cpu_usage()
            
            # 获取当前进程的内存占用情况
            process_info_memory = get_process_memory_usage()
            
            # 获取当前进程的硬盘写入情况
            process_info_disk_write = get_process_disk_write_usage()
            
            # 打印当前系统的CPU占用率
            print(f"System CPU Usage: {system_cpu_usage:.2f}%, CPU Temp: {cpu_temp:.2f}, Disk Free: {disk_free:.2f} GB")
            
            # 打印当前系统的内存占用情况
            print(f"System Memory Usage: {system_memory['percent']:.2f}% ({system_memory['used']:.2f} GB / {system_memory['total']:.2f} GB)")
            
            # 打印当前系统的硬盘写入情况
            print(f"System Disk (Current) Write: {system_disk_write:.2f} MB/s, Read: {system_disk_read:.2f} MB/s")

            # 打印当前系统的网络收发情况
            print(f"System Network Usage: Sent: {system_net_sent:.2f} MB/s, Received: {system_net_recv:.2f} MB/s")
            
            # 打印按CPU占用率排序的前10个进程
            msg["top_processes_by_cpu"] = print_top_processes_by_cpu(process_info_cpu)
            
            # 打印按内存占用量排序的前10个进程
            msg["top_processes_by_mem"] = print_top_processes_by_memory(process_info_memory)
            
            # 打印按硬盘写入量排序的前10个进程（当前每秒写入量）
            msg["top_processes_by_io"] = print_top_processes_by_disk_write(process_info_disk_write)

            msg["timestamp"] = time.time()
            pub.publish(msg)

            if args.tomcap:
                # 序列化 JSON 数据为二进制（utf-8 编码）
                json_bytes = json.dumps(msg, ensure_ascii=False).encode("utf-8")

                # 时间戳（纳秒，此处用示例数据中的 timestamp 乘以 1e9 转换为纳秒）
                timestamp_ns = int(msg["timestamp"] * 1e9)

                # 写入消息（log_time 和 publish_time 可设为同一时间戳）
                writer.add_message(
                    channel_id=channel_id,
                    data=json_bytes,
                    log_time=timestamp_ns,
                    publish_time=timestamp_ns,
                )

            # 每秒刷新一次
            r.sleep()

            # 清屏操作（适应终端显示）
            print("\033c", end="")
        except KeyboardInterrupt:
            print("\nCtrl+C detected, exiting program")
            pub.kill()
            break

    if args.tomcap:
        writer.finish()


if __name__ == "__main__":
    main()
    