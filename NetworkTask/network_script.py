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

if len(sys.argv) < 3 :
    print("Usage: network_processing.py <image_folder> <output_folder>")
    raise Exception("Invalid script arguments")

# Usage: network_processing.py <image_folder> <output_folder>
image_folder = sys.argv[1]
output_folder = sys.argv[2]

# ------- Settings -------------
process_network = True  # TODO: yaml
network_server = os.getenv("METASHAPE_SERVER") # TODO: 127.0.0.1 ip server master
Metashape.app.settings.network_path = '/home/photogrammetry/storage' # '/mnt/datasets'
photos = find_files(image_folder, [".jpg", ".jpeg", ".tif", ".tiff"])
# Configura il percorso di log globale
log_file_path = "/home/photogrammetry/storage/logs/funziona.txt"
Metashape.app.settings.log_path = log_file_path
Metashape.app.settings.log_enable = True

# -------New project and import photos-------------
doc = Metashape.Document()
doc.save(output_folder + 'project.psx')
chunk = doc.addChunk()
chunk.addPhotos(photos)
doc.save()
# --------------------

print(str(len(chunk.cameras)) + " images loaded")

tasks = []

has_reference = False
for c in chunk.cameras:
    if c.reference.location:
        has_reference = True

# ------- MatchPhotos -------------
task = Metashape.Tasks.MatchPhotos()
print("-- DEBUG: added Task:", task.name)
task.downscale = 1
task.keypoint_limit = 40000
task.tiepoint_limit = 10000
task.generic_preselection = True
task.reference_preselection = False
task.filter_stationary_points = True
task.keep_keypoints = True
task.guided_matching = False
task.subdivide_task = True
tasks.append(task)
# --------------------

# ------- AlignCameras -------------
task = Metashape.Tasks.AlignCameras()
print("-- DEBUG: added Task:", task.name)
task.adaptive_fitting = False
task.reset_alignment = True
task.subdivide_task = True
tasks.append(task)
# --------------------

# ------- BuildDepthMaps -------------
task = Metashape.Tasks.BuildDepthMaps()
print("-- DEBUG: added Task:", task.name)
task.downscale = 2
task.filter_mode = Metashape.MildFiltering
task.reuse_depth = False
task.subdivide_task = True
tasks.append(task)
# --------------------

if has_reference:
    # ------- BuildPointCloud -------------
    task = Metashape.Tasks.BuildPointCloud()
    print("-- DEBUG: added Task:", task.name)
    task.source_data = Metashape.DepthMapsData
    task.point_colors = True
    task.point_confidence = True
    task.keep_depth = True
    task.subdivide_task = True
    tasks.append(task)
    # --------------------

# ------- BuildModel -------------
task = Metashape.Tasks.BuildModel()
print("-- DEBUG: added Task:", task.name)
task.source_data = Metashape.DepthMapsData
task.surface_type = Metashape.Arbitrary
task.interpolation = Metashape.EnabledInterpolation
task.face_count = Metashape.HighFaceCount
task.vertex_colors = True
task.vertex_confidence = True
task.keep_depth = True
task.split_in_blocks = False
task.blocks_size = 250
task.build_texture = True
task.subdivide_task = True
tasks.append(task)
# --------------------

# ------- BuildUV -------------
task = Metashape.Tasks.BuildUV()
print("-- DEBUG: added Task:", task.name)
task.page_count = 1
task.mapping_mode = Metashape.GenericMapping
task.texture_size = 8192
tasks.append(task)
# --------------------

# ------- BuildTexture -------------
task = Metashape.Tasks.BuildTexture()
print("-- DEBUG: added Task:", task.name)
task.blending_mode = Metashape.MosaicBlending
task.texture_size = 8192
task.ghosting_filter = True
task.fill_holes = True
tasks.append(task)
# --------------------

if has_reference:
    # ------- BuildDem -------------
    task = Metashape.Tasks.BuildDem()
    print("-- DEBUG: added Task:", task.name)
    task.source_data = Metashape.PointCloudData
    task.interpolation = Metashape.EnabledInterpolation
    task.subdivide_task = True
    tasks.append(task)
    # --------------------

    # ------- BuildOrthomosaic -------------
    task = Metashape.Tasks.BuildOrthomosaic()
    print("-- DEBUG: added Task:", task.name)
    task.surface_data = Metashape.ElevationData
    task.fill_holes = True
    task.blending_mode = Metashape.MosaicBlending
    task.subdivide_task = True
    tasks.append(task)
    # --------------------

# ------- BuildTiledModel -------------
task = Metashape.Tasks.BuildTiledModel()
print("-- DEBUG: added Task:", task.name)
task.pixel_size = 0
task.tile_size = 256
task.source_data = Metashape.DepthMapsData
task.face_count = 20000
task.ghosting_filter = False
task.transfer_texture = False
task.keep_depth = True
task.subdivide_task = True
tasks.append(task)
# --------------------

task = Metashape.Tasks.ExportReport()
print("-- DEBUG: added Task:", task.name)
task.path = output_folder + '/report.pdf'
tasks.append(task)

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
    print(" --- DEGUB: batch_id", batch_id)
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

print("End process network")