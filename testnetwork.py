import Metashape
import sys, os

if Metashape.app.activated:
    print("-- Metashape is activated: ", Metashape.app.activated)
else:
    raise Exception("No license found.")

compatible_major_version = "2.1"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

# Usage: network_processing.py <image_folder> <output_folder>
image_folder = sys.argv[1]
output_folder = sys.argv[2]

# Settings
process_network = True  # TODO: yaml
network_server = os.getenv("METASHAPE_SERVER") # TODO: è dinamico? richiedo questo da input o yaml settings?
Metashape.app.settings.network_path = '/home/photogrammetry/storage' #'/mnt/datasets'
photos = find_files(image_folder, [".jpg", ".jpeg", ".tif", ".tiff"])

# -------New project and import photos-------------
doc = Metashape.Document()
doc.save(output_folder + 'progetto.psx')
chunk = doc.addChunk()
chunk.addPhotos(photos)
doc.save()
# --------------------

print(str(len(chunk.cameras)) + " images loaded")

tasks = []
# -------primo task-------------
task = Metashape.Tasks.MatchPhotos()
print("-- DEGUB: added", task.name)
task.keypoint_limit = 40000
task.tiepoint_limit = 10000
task.generic_preselection = True
task.reference_preselection = True
tasks.append(task)
# --------------------

if process_network:
    # Rendo tutti i task Network task
    print("Rendo tutti i task network task")
    network_tasks = []
    for task in tasks:
        if task.target == Metashape.Tasks.DocumentTarget:
            network_tasks.append(task.toNetworkTask(doc))
        else:
            network_tasks.append(task.toNetworkTask(chunk))

    client = Metashape.NetworkClient()
    client.connect(network_server)
    batch_id = client.createBatch(doc.path, network_tasks)
    client.setBatchPaused(batch_id, False)

    print('Processing started, results will be saved to ' + output_folder + '.')
else:
    # non è network
    for task in tasks:
        if task.target == Metashape.Tasks.DocumentTarget:
            task.apply(doc) # progress printer
        else:
            task.apply(chunk) # progress printer

    print('Processing finished, results saved to ' + output_folder + '.')

print('Processing finished really, results saved to ' + output_folder + '.')