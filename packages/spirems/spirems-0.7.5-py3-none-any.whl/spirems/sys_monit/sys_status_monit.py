#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import psutil
import time
import socket
import json
from spirems.publisher import Publisher
from spirems.msg_helper import def_msg
from spirems import CSVLogger
from spirems.logsaver import LoggerSaver, LogType

global g_status
g_status = dict()


def get_mem_by_pid(pid):
    try:
        process = psutil.Process(pid)
        mem_mb = process.memory_info().rss / 1024 / 1024
    except:
        mem_mb = 0.0
    return mem_mb


def get_cpu_by_pid(pid):
    try:
        process = psutil.Process(pid)
        cpu = process.cpu_percent(interval=0.01)
    except:
        cpu = 0.0
    return cpu


def cpu_monit():
    global g_status
    status = dict()
    cpu_cnt = psutil.cpu_count()
    # print("cpu_count: {}".format(cpu_cnt))
    cpu_percent = psutil.cpu_percent(interval=0.1)
    # print("cpu_percent: {}".format(cpu_percent))
    status["cpu"] = cpu_percent
    # cpu_freq = psutil.cpu_freq(percpu=False)
    # print("cpu_freq: {}".format(cpu_freq))

    virtual_memory = psutil.virtual_memory()
    # logger.debug("virtual_memory: {}".format(virtual_memory))
    memory_total_gb = virtual_memory.total / 1024 / 1024 / 1024
    memory_available_gb = virtual_memory.available / 1024 / 1024 / 1024
    status["memory"] = round(1.0 - memory_available_gb / memory_total_gb, 3)

    net_io_counters = psutil.net_io_counters()
    net_r = net_io_counters.bytes_recv / 1024 / 1024
    net_s = net_io_counters.bytes_sent / 1024 / 1024
    if 'net_t' in g_status:
        net_dt = time.time() - g_status['disk_t']
        status["net_r_mbps"] = round((net_r - g_status['net_r_mb']) / net_dt, 3)
        status["net_s_mbps"] = round((net_s - g_status['net_s_mb']) / net_dt, 3)
    else:
        status["net_r_mbps"] = 0
        status["net_s_mbps"] = 0
    g_status['net_t'] = time.time()
    g_status['net_r_mb'] = net_r
    g_status['net_s_mb'] = net_s

    disk_usage = psutil.disk_usage('/')
    # print("disk_usage: {}".format(disk_usage))
    disk_total_gb = disk_usage.total / 1024 / 1024 / 1024
    disk_free_gb = disk_usage.free / 1024 / 1024 / 1024
    status["disk"] = round(1.0 - disk_free_gb / disk_total_gb, 3)

    disk_io_counters = psutil.disk_io_counters(perdisk=False)
    # print("disk_io_counters: {}".format(disk_io_counters))
    disk_r = disk_io_counters.read_bytes / 1024 / 1024
    disk_w = disk_io_counters.write_bytes / 1024 / 1024
    if 'disk_t' in g_status:
        disk_dt = time.time() - g_status['disk_t']
        status["disk_r_mbps"] = round((disk_r - g_status['disk_r_mb']) / disk_dt, 3)
        status["disk_w_mbps"] = round((disk_w - g_status['disk_w_mb']) / disk_dt ,3)
    else:
        status["disk_r_mbps"] = 0
        status["disk_w_mbps"] = 0
    g_status['disk_t'] = time.time()
    g_status['disk_r_mb'] = disk_r
    g_status['disk_w_mb'] = disk_w

    sensors_temperatures = psutil.sensors_temperatures()
    if 'coretemp' in sensors_temperatures:
        status['cpu_temp'] = sensors_temperatures['coretemp'][0].current
    elif 'k10temp' in sensors_temperatures:
        status['cpu_temp'] = sensors_temperatures['k10temp'][0].current
    
    status['timestamp'] = time.time()

    # pids = psutil.pids()
    proc_names = dict()
    for proc in psutil.process_iter(['pid', 'name']):
        name = proc.info['name']
        if name in proc_names:
            proc_names[name].append(proc.info['pid'])
        else:
            proc_names[name] = [proc.info['pid']]

    top_names = dict()
    top_k = min(len(proc_names), 10)
    for name, pids in proc_names.items():
        t_mem_mb = 0.0
        for pid in pids:
            t_mem_mb += get_mem_by_pid(pid)
        top_names[name] = round(t_mem_mb, 2)
    
    top_names = dict(sorted(top_names.items(), key=lambda item: item[1], reverse=True)[:top_k])
    """
    for name in top_names.keys():
        t_cpu = 0.0
        for pid in proc_names[name]:
            t_cpu += get_cpu_by_pid(pid)
        top_names[name] = [round(top_names[name], 2), round(t_cpu / cpu_cnt, 2)]
    """
    status['top_procs'] = top_names

    return status


class UDPServer:
    def __init__(
        self,
        port: int = 9990
    ):
        self.ip = "0.0.0.0"
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, json_dict):
        try:
            json_data = json.dumps(json_dict).encode('utf-8')
            self.sock.sendto(json_data, (self.ip, self.port))
        except:
            self.sock.close()


def status_pub():
    global g_status
    ls = LoggerSaver(
        save_path='',
        log_type=LogType.CSVLog,
        name='SystemStatus'
    )
    udp = UDPServer()
    pub = Publisher('/system/status', 'std_msgs::Null')
    logger = CSVLogger(['timestamp', 'cpu', 'cpu_temp', 'memory', 'disk', 'net_r_mbps', 'net_s_mbps', 'disk_r_mbps', 'disk_w_mbps'], name='SystemStatus')

    while True:
        # time.sleep(1)
        msg_num = def_msg('std_msgs::Null')
        status = cpu_monit()
        logger.append([status['timestamp'], status['cpu'], status['cpu_temp'], status['memory'], status['disk'], status['net_r_mbps'], status['net_s_mbps'], status['disk_r_mbps'], status['disk_w_mbps']])
        msg_num.update(status)
        del status['top_procs']
        udp.send(status)
        pub.publish(msg_num)


if __name__ == '__main__':
    status_pub()
