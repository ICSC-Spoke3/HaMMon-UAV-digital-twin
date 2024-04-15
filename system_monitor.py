import logging
import psutil
import csv
import time
import threading
import subprocess

class SystemMonitor:
    def __init__(self, module_name, log_file):
        logging.basicConfig(filename=log_file, level=logging.INFO, filemode='a')
        self.logger = logging.getLogger(module_name)
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            cpu_usage, cpu_core_usage = self.log_cpu()
            ram_usage, ram_available, size_available, ram_active, size_active = self.log_ram()
            stats = self.log_gpu()
            for stat in stats:
                self.logger.info(f'{time.time()}, {cpu_usage}, {cpu_core_usage}, {ram_usage}, {ram_available} {size_available}, {ram_active} {size_active}, {stat["id"]}, {stat["model"]}, {stat["temp"]}, {stat["cpu_usage"]}, {stat["mem_used"]}/{stat["mem_total"]} MB')
            time.sleep(5)  # every 5 sec

    def stop(self):
        self.running = False
    
    def create_csv(self, log_file):
        header = ['Level', 'Modulo', 'Time', 'CPU usage %', 'Cores usage %', 'RAM usage %', 'RAM used', 'RAM active', 'GPU ID', 'GPU Model', 'GPU Temp', 'GPU Core %', 'GPU RAM']
        with open(log_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

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
        lines = gpustat_output.split('\n')
        stats = []
        for i, line in enumerate(lines):
            if line and i % 2 != 0: # check empty row
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
        cpu_usage = psutil.cpu_percent(interval=None, percpu=False) # avg from last call (delta_t)
        cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)    # percpu floating for each core cpu
        return cpu_usage, cpu_core_usage

    def log_ram(self):
        ram_usage = psutil.virtual_memory().percent
        ram_available, size_available  = self.parese_dataram(psutil.virtual_memory().available)
        ram_active, size_active = self.parese_dataram(psutil.virtual_memory().active)
        return ram_usage, ram_available, size_available, ram_active, size_active
        
    def log_gpu(self):
        result = subprocess.run(['gpustat'], stdout=subprocess.PIPE)
        stats_str = result.stdout.decode('utf-8')
        stats = self.parse_gpustat(stats_str)
        return stats

#monitor = SystemMonitor('SystemMonitor', 'system.csv')
#monitor.create_csv(log_file='system.csv')
#thread = threading.Thread(target=monitor.start)
#thread.start()
#time.sleep(20)
#monitor.stop()