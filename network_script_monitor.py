import Metashape
import sys, os, csv, time
import psutil

# Funzione per monitorare le risorse
def monitor_resources(output_csv, client, batch_id, interval=5):
    """
    Monitora le risorse del sistema e registra lo stato dei task.

    Args:
        output_csv (str): Percorso del file CSV per salvare i dati.
        client (Metashape.NetworkClient): Istanza del client Metashape.
        batch_id (int): ID del batch di task in esecuzione.
        interval (int): Intervallo di campionamento in secondi.
    """
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Time", "Task_Name", "Task_Status", "CPU_Usage", "RAM_Usage_MB", "GPU_Usage", "GPU_Memory_Used_MB"])
        
        try:
            while True:
                # Stato corrente del batch e task
                batch_info = client.batchInfo(batch_id)
                current_task = batch_info['active_task_name'] if 'active_task_name' in batch_info else "Unknown"
                task_status = batch_info['status'] if 'status' in batch_info else "Unknown"
                # active_task_name: il nome del task attivo.
                # status: lo stato complessivo del batch.

                # Monitoraggio delle risorse
                cpu_usage = psutil.cpu_percent(interval=0)
                ram_usage = psutil.virtual_memory().used / (1024 ** 2)  # Convert to MB
                gpu_usage = 0  # Placeholder per GPU
                gpu_memory = 0

                # Monitoraggio GPU (richiede pynvml per GPU NVIDIA)
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # Prima GPU
                    gpu_usage = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                    gpu_memory = pynvml.nvmlDeviceGetMemoryInfo(handle).used / (1024 ** 2)  # Convert to MB
                    pynvml.nvmlShutdown()
                except ImportError:
                    pass
                
                # Scrittura nel file CSV
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), current_task, task_status, cpu_usage, ram_usage, gpu_usage, gpu_memory])
                time.sleep(interval)
                
                # Interruzione al completamento
                if task_status.lower() == "completed":
                    print("Tutti i task completati.")
                    break
        except KeyboardInterrupt:
            print("Monitoraggio terminato.")

# --- Integrazione con il workflow esistente ---
if Metashape.app.activated:
    print("-- Metashape is activated: ", Metashape.app.activated)
else:
    raise Exception("No license found.")

compatible_major_version = "2.1"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception(f"Incompatible Metashape version: {found_major_version} != {compatible_major_version}")

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

if len(sys.argv) < 3:
    print("Usage: network_processing.py <image_folder> <output_folder>")
    raise Exception("Invalid script arguments")

image_folder = sys.argv[1]
output_folder = sys.argv[2]
resource_log_path = os.path.join(output_folder, "resource_monitoring.csv")

# ------- Settings -------------
process_network = True
network_server = '127.0.0.1'
Metashape.app.settings.network_path = '/mnt/datasets'
photos = find_files(image_folder, [".jpg", ".jpeg", ".tif", ".tiff"])

# ------- New project and import photos -------------
doc = Metashape.Document()
doc.save(output_folder + 'project.psx')
chunk = doc.addChunk()
chunk.addPhotos(photos)
doc.save()
print(str(len(chunk.cameras)) + " images loaded")

tasks = []

# Creazione task Metashape...
# -- qui includi i task del tuo script originale --

if process_network:
    print("Rendo tutti i task network task")
    network_tasks = [task.toNetworkTask(doc) if task.target == Metashape.Tasks.DocumentTarget else task.toNetworkTask(chunk) for task in tasks]

    client = Metashape.NetworkClient()
    client.connect(network_server)
    batch_id = client.createBatch(doc.path, network_tasks)
    client.setBatchPaused(batch_id, False)

    print("Avvio il monitoraggio delle risorse...")
    monitor_resources(resource_log_path, client, batch_id)
    
    print('Processing started, results will be saved to ' + output_folder + '.')
else:
    for task in tasks:
        if task.target == Metashape.Tasks.DocumentTarget:
            task.apply(doc)
        else:
            task.apply(chunk)
    print('Processing finished, results saved to ' + output_folder + '.')

print("Il processo è finito.")
