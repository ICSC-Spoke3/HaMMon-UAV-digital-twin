import logging
import psutil
import csv
import time
import threading
import subprocess

"""
Sistema per il monitoraggio dei task svolti.
"""

class SystemMonitor:
    # log_file: file csv 
    # time: sec 
    def __init__(self, log_file: str, time: int = 30) -> None:
        logging.basicConfig(filename=log_file, level=logging.INFO, filemode='a', format='%(name)s;%(message)s')
        self.logger = None
        self.running = False
        self.time = time
        self.log_file = log_file

        self.create_csv()

    def start(self, module_name: str) -> None:
        self.running = True
        self.logger = module_name
        while self.running:
            cpu_usage, cpu_core_usage = self.log_cpu()
            ram_usage, ram_total, ram_available, ram_active, ram_used = self.log_ram()
            gpu_info = self.log_gpu()
            gpu_info_filter = [{entry: info[entry] for entry in ('temp', 'cpu_usage', 'mem_used')} for info in gpu_info]
            self.logger.info(f'{time.time()}; {cpu_usage}; {cpu_core_usage}; {ram_usage}; {ram_active} GB; {ram_total} GB; {ram_available} GB; {ram_used} GB; {gpu_info_filter}')
            #for stat in stats:
                # self.logger.info(f'{time.time()}; {cpu_usage}; {cpu_core_usage}; {ram_usage}; {ram_active} GB; {ram_total} GB; {ram_available} GB; {ram_used} GB; {stat["id"]}; {stat["model"]}; {stat["temp"]}; {stat["cpu_usage"]}; {stat["mem_used"]}/{stat["mem_total"]} MB')
            time.sleep(self.time)  # every 30 sec

    def stop(self):
        self.running = False
    
    def create_csv(self):
        header = ['Modulo', 'Time', 'CPU usage %', 'Cores usage %', 'RAM usage %', 'RAM active', 'RAM total', 'RAM Available', 'RAM Used']
        gpu_info = self.log_gpu()   # get gpu header info
        header_info = [f'GPUs: {[{entry: info[entry] for entry in ("id", "model", "mem_total")} for info in gpu_info]}']

        with open(self.log_file, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(header + header_info)

    def parese_dataram(self, ram_memory):
        # Convert in GB and exclude the decimal part
        ram_memory = ram_memory / (1024 * 1024 * 1024)
        return ram_memory
    
    def parse_gpustat(self, gpustat_output):
        lines = gpustat_output.split('\n')
        stats = []
        for i, line in enumerate(lines):
            if line and i != 0: # check empty row and avoid timestamp row
                parts = line.split("|")
                id_gpumodel = parts[0].split()
                temp_gpu = parts[1].split()
                memgpu = parts[2].split()
                stat = {
                    'id': id_gpumodel[0],
                    'model': ''.join(id_gpumodel[1:]),
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
        ram_total = self.parese_dataram(psutil.virtual_memory().total)
        ram_available = self.parese_dataram(psutil.virtual_memory().available)
        ram_active = self.parese_dataram(psutil.virtual_memory().active)
        ram_used = self.parese_dataram(psutil.virtual_memory().used)
        return ram_usage, ram_total, ram_available, ram_active, ram_used
        
    def log_gpu(self):
        result = subprocess.run(['gpustat'], stdout=subprocess.PIPE)
        stats_str = result.stdout.decode('utf-8')
        stats = self.parse_gpustat(stats_str)
        return stats

if __name__ == "__main__":
    monitor = SystemMonitor('system.csv')
    thread = threading.Thread(target=monitor.start, args=('TestSystemMonitor',))
    thread.start()
    time.sleep(20)
    monitor.stop()