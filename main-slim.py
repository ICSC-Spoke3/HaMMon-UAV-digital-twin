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
        print("=========",image_folder)
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

print(str(len(chunk.cameras)) + " images loaded")

print("--Matching Photos 4")
progress_printer = ProgressPrinter("matchPhotos")
chunk.matchPhotos(keypoint_limit = 40000, 
                  tiepoint_limit = 10000, 
                  generic_preselection = True, 
                  reference_preselection = True,
                  progress=progress_printer) # Progress callback
doc.save()

print("--Aligning Cameras 5")
chunk.alignCameras()
doc.save()

progress_printer = ProgressPrinter("buildDeptMaps")
chunk.buildDepthMaps(
                downscale = 2,
                filter_mode = Metashape.MildFiltering, 
                reuse_depth = True,
                progress = progress_printer)
doc.save()

progress_printer = ProgressPrinter("buildModel")
chunk.buildModel(source_data = Metashape.DepthMapsData,
                 surface_type = Metashape.HeightField,
                 face_count = Metashape.HighFaceCount,
                 interpolation = Metashape.DisabledInterpolation,
                 vertex_color = True,
                 progress = progress_printer)
doc.save()

print("--Building UV 7")
progress_printer = ProgressPrinter("buildUV")
chunk.buildUV(page_count = 2, 
              texture_size = 4096,
              progress = progress_printer)
doc.save()

print("--Building Texture 8")
progress_printer = ProgressPrinter("buildTexture")
chunk.buildTexture(blending_mode = Metashape.MosaicBlending,
                   texture_size = 4096,
                   fill_holes = True, 
                   ghosting_filter = True, 
                   progress = progress_printer)
doc.save()

has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation

# or directly check reference on cameras
"""
has_reference = False
for c in chunk.cameras:
    if c.reference.location:
        has_reference = True
"""

if has_transform:
    print("--Building Point Cloud (has_transform) 9")
    progress_printer = ProgressPrinter("buildPointCloud")
    chunk.buildPointCloud(
        point_colors = True, 
        point_confidence = True, 
        keep_depth = True,
        progress = progress_printer)
    doc.save()

    print("--Building Dem (has_transform) 10")
    chunk.buildDem(source_data = Metashape.PointCloudData,
                   interpolation = Metashape.EnabledInterpolation, 
                   progress = progress_printer)
    doc.save()

    print("--Building Orthomosaic (has_transform) 11")
    progress_printer = ProgressPrinter("buildOrthomosaic")
    chunk.buildOrthomosaic(surface_data = Metashape.ElevationData, progress = progress_printer)
    doc.save()

print("--Exporting results")
# export results
chunk.exportReport(output_folder + '/report.pdf')

if chunk.model:
    print("--Exporting Model")
    chunk.exportModel(output_folder + '/model.obj')

if chunk.point_cloud:
    print("--Exporting Point Cloud")
    chunk.exportPointCloud(output_folder + '/point_cloud.las', source_data = Metashape.PointCloudData)

if chunk.elevation:
    print("--Exporting Elevation")
    chunk.exportRaster(output_folder + '/dem.tif', source_data = Metashape.ElevationData)

if chunk.orthomosaic:
    print("--Exporting Orthomosaic")
    chunk.exportRaster(output_folder + '/orthomosaic.tif', source_data = Metashape.OrthomosaicData, split_in_blocks=True)

print('Processing finished, results saved to ' + output_folder + '.')
Metashape.app.quit()