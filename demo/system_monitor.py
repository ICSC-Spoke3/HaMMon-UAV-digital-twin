import logging
import psutil
import csv
import time
import threading
import subprocess

class SystemMonitor:
    def __init__(self, module_name, log_file):
        logging.basicConfig(filename=log_file, level=logging.INFO, filemode='a', format='%(name)s;%(message)s')
        self.logger = logging.getLogger(module_name)
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            cpu_usage, cpu_core_usage = self.log_cpu()
            ram_usage, ram_total, ram_available, ram_active, ram_used = self.log_ram()
            gpu_info = self.log_gpu()
            gpu_info_filter = [{entry: info[entry] for entry in ('temp', 'cpu_usage', 'mem_used')} for info in gpu_info]
            self.logger.info(f'{time.time()}; {cpu_usage}; {cpu_core_usage}; {ram_usage}; {ram_active} GB; {ram_total} GB; {ram_available} GB; {ram_used} GB; {gpu_info_filter}')
            #for stat in stats:
                # self.logger.info(f'{time.time()}; {cpu_usage}; {cpu_core_usage}; {ram_usage}; {ram_active} GB; {ram_total} GB; {ram_available} GB; {ram_used} GB; {stat["id"]}; {stat["model"]}; {stat["temp"]}; {stat["cpu_usage"]}; {stat["mem_used"]}/{stat["mem_total"]} MB')
            time.sleep(30)  # every 30 sec

    def stop(self):
        self.running = False
    
    def create_csv(self, log_file):
        header = ['Modulo', 'Time', 'CPU usage %', 'Cores usage %', 'RAM usage %', 'RAM active', 'RAM total', 'RAM Available', 'RAM Used']
        gpu_info = self.log_gpu()   # get gpu header info
        header_info = [f'GPUs: {[{entry: info[entry] for entry in ("id", "model", "mem_total")} for info in gpu_info]}']

        with open(log_file, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(header + header_info)

    def parese_dataram(self, ram_memory):
        # Convert in GB and exclude the decimal part
        ram_memory = ram_memory / (1024 * 1024 * 1024)
        print(type(ram_memory))
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
        print(type(stats))
        return stats

    def log_cpu(self):
        cpu_usage = psutil.cpu_percent(interval=None, percpu=False) # avg from last call (delta_t)
        cpu_core_usage = psutil.cpu_percent(interval=None, percpu=True)    # percpu floating for each core cpu
        print(type(cpu_usage), type(cpu_core_usage))
        return cpu_usage, cpu_core_usage

    def log_ram(self):
        ram_usage = psutil.virtual_memory().percent
        ram_total = self.parese_dataram(psutil.virtual_memory().total)
        ram_available = self.parese_dataram(psutil.virtual_memory().available)
        ram_active = self.parese_dataram(psutil.virtual_memory().active)
        ram_used = self.parese_dataram(psutil.virtual_memory().used)
        print(type(ram_usage), type(ram_total), type(ram_available), type(ram_active), type(ram_used))
        return ram_usage, ram_total, ram_available, ram_active, ram_used
        
    def log_gpu(self):
        result = subprocess.run(['gpustat'], stdout=subprocess.PIPE)
        stats_str = result.stdout.decode('utf-8')
        stats = self.parse_gpustat(stats_str)
        print(type(stats))
        return stats

if __name__ == "__main__":
    monitor = SystemMonitor('SystemMonitor', 'system.csv')
    monitor.create_csv(log_file='system.csv')
    thread = threading.Thread(target=monitor.start)
    thread.start()
    time.sleep(20)
    monitor.stop()