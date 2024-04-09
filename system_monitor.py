import logging
import psutil
import re
import time
import threading
import subprocess

class SystemMonitor:
    def __init__(self, module_name, log_file):
        logging.basicConfig(filename=log_file, level=logging.INFO, filemode='w')
        self.logger = logging.getLogger(module_name)
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            self.log_cpu()
            self.log_ram()
            self.log_gpu()
            time.sleep(5)  # Every 5 sec

    def stop(self):
        self.running = False

    def parese_dataram(self, ram_memory):
        # Convert in GB and exclude the decimal part
        ram_memory = int(ram_memory / 1024 / 1024)
        size = 'GB'
        if ram_memory < 1000:
            size = 'MB'
        # Add a thousand separator
        ram_memory = "{:,}".format(ram_memory)
        return ram_memory, size
    
    def parse_gpustat(self, gpustat_output):
        lines = gpustat_output.split('\n')  # Suddividi l'output in righe
        stats = []
        for i, line in enumerate(lines):
            if line:  # Ignora le righe vuote
                if i % 2 == 0:
                    parts = line.split()
                    stat = {
                        'node': parts[0],
                        'week_day': parts[1],
                        'month': parts[2],
                        'number_day': parts[3],
                        'time': parts[4],
                        'year': parts[5],
                        'idk': parts[6]
                    }
                else:
                    parts = line.split("|")
                    id_gpumodel = parts[0].split()
                    temp_gpu = parts[1].split()
                    memgpu = parts[2].split()
                    stat = {
                        'id': id_gpumodel[0],
                        'model': ' '.join(id_gpumodel[1:]),
                        'temp': temp_gpu[0][:-1],
                        'cpu_usage': ''.join(temp_gpu[1:]),
                        'mem_used': memgpu[0],
                        'mem_total': ''.join(memgpu[2:])
                    }
                stats.append(stat)
        return stats


    def log_cpu(self):
        cpu_usage = psutil.cpu_percent(interval=0.1, percpu=True)    # percpu percentuale in floating per singola cpu ritorna una lista
        self.logger.info(f'CPU usage: {cpu_usage}%, CPUs (physical: {psutil.cpu_count(logical=False)}, logical: {psutil.cpu_count(logical=True)})')
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            if proc.info['memory_info'] is not None and proc.info['memory_info'].rss != 0 and 'metashape' in proc.info['name']:
                pid = proc.info['pid']
                name = proc.info['name']
                ram_rss_test = proc.info['memory_info'].rss
                ram_vms_test = proc.info['memory_info'].vms
                ram_rss, size_rss = self.parese_dataram(proc.info['memory_info'].rss)
                ram_vms, size_vms = self.parese_dataram(proc.info['memory_info'].vms)
                """
                ram_shared, size_shared = self.formatter(proc.info['memory_info'].shared)
                ram_text, size_text = self.formatter(proc.info['memory_info'].text)
                ram_lib, size_lib = self.formatter(proc.info['memory_info'].lib)
                ram_data, size_data = self.formatter(proc.info['memory_info'].data)
                ram_dirty, size_dirty = self.formatter(proc.info['memory_info'].dirty)
                self.logger.info(f'Proces-ID: {pid}, Name: {name} (RSS: {ram_rss}{size_rss}, VMS: {ram_vms}{size_vms}, SHARED: {ram_shared}{size_shared}, TEXT: {ram_text}{size_text})')
                """
                self.logger.info(f'Proces-ID: {pid}, Name: {name} (RSS: {ram_rss_test}{size_rss}, VMS: {ram_vms_test}{size_vms})')

    def log_ram(self):
        ram_usage = psutil.virtual_memory().percent
        ram_available, size_available  = self.parese_dataram(psutil.virtual_memory().available)
        ram_used, size_used = self.parese_dataram(psutil.virtual_memory().used)
        ram_active, size_active = self.parese_dataram(psutil.virtual_memory().active)
        
        self.logger.info(f'RAM usage: {ram_usage}%, RAM used: {ram_used}{size_used}, RAM available: {ram_available}{size_available}, RAM active: {ram_active}{size_active}')

    def log_gpu(self):
        result = subprocess.run(['gpustat'], stdout=subprocess.PIPE)
        stats_str = result.stdout.decode('utf-8')
        stats = self.parse_gpustat(stats_str)

        for i, stat in enumerate(stats):
            if i % 2 != 0:
                log_message = f"GPU ID: {stat['id']}, Model: {stat['model']}, Temp: {stat['temp']}, CPU Usage: {stat['cpu_usage']}, Memory: {stat['mem_used']}/{stat['mem_total']} MB"
                self.logger.info(log_message)

monitor = SystemMonitor('SystemMonitor', 'system.log')
thread = threading.Thread(target=monitor.start)
thread.start()
time.sleep(20)
monitor.stop()
