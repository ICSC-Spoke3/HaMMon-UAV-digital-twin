import Metashape
from demo.progress_printer import ProgressPrinter
import os, sys, datetime

# Checking compatibility
compatible_major_version = "2.1"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

# manage input parameters
try:
    if len(sys.argv) < 2:
        print("Usage: main.py <image_folder> [output_folder]")
        raise Exception("Invalid script arguments")
    image_folder = sys.argv[1]

    # check image_folder exist
    if not os.path.isdir(image_folder):
        raise FileNotFoundError(f"{image_folder} does not exist")
    
    # only image_folder
    if len(sys.argv) == 2:
        # default output folder path
        output_folder_name = os.path.basename(image_folder) + '_' + datetime.datetime.now().strftime("%d%m_%H%M")
        output_folder = os.path.join('../', output_folder_name)
        os.makedirs(output_folder, exist_ok=True)
        
    # image e output
    if len(sys.argv) == 3:
        output_folder = sys.argv[2]
        # if output_folder do not exist, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    if len(sys.argv) >= 4:
        raise Exception("Too much input arguments")
    
except Exception as e:
    print(f"Error: {str(e)}")

photos = find_files(image_folder, [".jpg", ".jpeg", ".tif", ".tiff"])

# Settings preference:
# disable CPU when performing GPU accelerated processing
Metashape.app.cpu_enable = False

print("--Creating Project 1")
doc = Metashape.Document()
doc.save(output_folder + '/project.psx')

print("--Adding Chunk 2")
chunk = doc.addChunk()

print("--Adding Photos 3")
chunk.addPhotos(photos)
doc.save()

# estimate image quality
for camera in chunk.cameras:
    chunk.analyzePhotos(camera)
    if float(camera.photo.meta['Image/Quality']) < 0.5:
         camera.enabled = False
doc.save()

print(str(len(chunk.cameras)) + " images loaded")

print("--Matching Photos 4")
progress_printer = ProgressPrinter("matchPhotos")
chunk.matchPhotos(keypoint_limit = 40000, 
                  tiepoint_limit = 10000, 
                  generic_preselection = True, 
                  reference_preselection = True,
                  progress=progress_printer) # Progress callback
doc.save()

chunk.alignCameras()
doc.save()

chunk.buildDepthMaps(downscale = 2, filter_mode = Metashape.MildFiltering)
doc.save()

chunk.buildModel(source_data = Metashape.DepthMapsData)
doc.save()

chunk.buildUV(page_count = 2, texture_size = 4096)
doc.save()

chunk.buildTexture(texture_size = 4096, ghosting_filter = True)
doc.save()

has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

if has_transform:
    chunk.buildPointCloud()
    doc.save()

    chunk.buildDem(source_data=Metashape.PointCloudData)
    doc.save()

    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData)
    doc.save()

# export results
chunk.exportReport(output_folder + '/report.pdf')

if chunk.model:
    chunk.exportModel(output_folder + '/model.obj')

if chunk.point_cloud:
    chunk.exportPointCloud(output_folder + '/point_cloud.las', source_data = Metashape.PointCloudData)

if chunk.elevation:
    chunk.exportRaster(output_folder + '/dem.tif', source_data = Metashape.ElevationData)

if chunk.orthomosaic:
    chunk.exportRaster(output_folder + '/orthomosaic.tif', source_data = Metashape.OrthomosaicData)

print('Processing finished, results saved to ' + output_folder + '.')