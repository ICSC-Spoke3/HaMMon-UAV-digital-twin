import Metashape
from progress_printer import ProgressPrinter
from system_monitor import SystemMonitor
import os, sys, datetime, threading, subprocess


# Checking compatibility: to remove if it give trubleshooting
compatible_major_version = "2.1"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

# manage input parameters
try:
    if len(sys.argv) < 2:
        print("Usage: demo_process.py <image_folder> [output_folder]")
        raise Exception("Invalid script arguments")
    image_folder = sys.argv[1]

    # check image_folder exist
    if not os.path.isdir(image_folder):
        raise FileNotFoundError(f"{image_folder} does not exist")
    
    # only image_folder
    if len(sys.argv) == 2:
        # Save on Moduli
        output_folder_name = os.path.basename(image_folder) + '_' + datetime.datetime.now().strftime("%d%m_%H%M")
        output_folder = os.path.join('/storage/Metashape_Hammon/Modelli', output_folder_name)
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

# check presence of image in image_folder
photos = find_files(image_folder, [".jpg", ".jpeg", "jp2", "j2k", "jxl", ".tif", ".tiff", ".png", ".bmp", ".exr", ".tga", ".pgm", ".ppm", ".dng", ".mpo", ".seq", ".ara"])

# Monitoring setup
monitor = SystemMonitor('New Project', 'system.csv')
monitor.create_csv(log_file='system.csv')
thread = threading.Thread(target=monitor.start)
thread.start()

print("--Creating Project 1")
doc = Metashape.Document()
doc.save(output_folder + '/project.psx')
chunk = doc.addChunk()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('addPhotos', 'system.csv')
thread = threading.Thread(target=monitor.start)
thread.start()

print("--Adding Photos 2")
progress_printer = ProgressPrinter("addPhotos")
chunk.addPhotos(filenames=photos,
                progress=progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

print(str(len(chunk.cameras)) + " images loaded")

# missing analyzeImages
# missing optimizeCameras

# Monitoring setup
monitor = SystemMonitor('matchPhotos', 'system.csv')
thread = threading.Thread(target=monitor.start)
thread.start()

print("--Matching Photos 3")
progress_printer = ProgressPrinter("matchPhotos")
chunk.matchPhotos(downscale=1,
                  keypoint_limit = 40000, 
                  tiepoint_limit = 10000, 
                  generic_preselection = True, 
                  reference_preselection = False,
                  filter_stationary_points = True,
                  guided_matching= False,
                  subdivide_task= True,
                  progress=progress_printer) # Progress callback
doc.save()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('alignCameras', 'system.csv')
thread = threading.Thread(target=monitor.start)
thread.start()

print("--Align Cameras 4")
progress_printer = ProgressPrinter("alignCameras")
chunk.alignCameras(adaptive_fitting= False,
                   reset_alignment= False,
                   subdivide_task=True,
                   progress= progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('buildDepthMaps', 'system.csv')
thread = threading.Thread(target=monitor.start)
thread.start()

print("--Build Depth Maps 5")
progress_printer = ProgressPrinter("buildDepthMaps")
chunk.buildDepthMaps(downscale = 2,
                     filter_mode = Metashape.MildFiltering,
                     reuse_depth= False,
                     subdivide_task=True,
                     progress=progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

has_transform = chunk.transform.scale and chunk.transform.rotation and chunk.transform.translation
# 4x4 matrix specifying chunck location in the world coordinate system
# scale: scale component 
# rotation: rotation component
# translation: translation component
if has_transform:

    # Monitoring setup
    monitor = SystemMonitor('buildPointCloud', 'system.csv')
    thread  = threading.Thread(target=monitor.start)
    thread.start()

    print("--Build Point Cloud 6")
    progress_printer = ProgressPrinter("buildPointCloud")
    chunk.buildPointCloud(source_data=Metashape.DepthMapsData,
                          point_colors=True,
                          point_confidence=True,
                          keep_depth=True,
                          subdivide_task=True,
                          progress=progress_printer)
    # point spacing default = 0.1(m)
    doc.save()

    monitor.stop()
    thread.join()   # wait thread end

    # Monitoring setup
    monitor = SystemMonitor('colorizePointCloud', 'system.csv')
    thread  = threading.Thread(target=monitor.start)
    thread.start()

    print("--Colorize Point Cloud 7")
    progress_printer = ProgressPrinter("colorizePointCloud")
    chunk.colorizePointCloud(source_data=Metashape.ImagesData,
                             subdivide_task=True,
                             progress=progress_printer)
    doc.save()

    monitor.stop()
    thread.join()   # wait thread end

    # missing filterPointCloud

# Monitoring setup
monitor = SystemMonitor('buildModel', 'system.csv')
thread  = threading.Thread(target=monitor.start)
thread.start()

print("--Build Model 8")
progress_printer = ProgressPrinter("buildModel")
chunk.buildModel(surface_type=Metashape.Arbitrary,
                 source_data = Metashape.DepthMapsData,
                 interpolation=Metashape.EnabledInterpolation,
                 face_count= Metashape.HighFaceCount,
                 vertex_colors=True,
                 vertex_confidence=True,
                 keep_depth=True,
                 build_texture= True,
                 subdivide_task=True,
                 progress=progress_printer)
# split in block
doc.save()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('colorizeModel', 'system.csv')
thread  = threading.Thread(target=monitor.start)
thread.start()

print("--Colorize Model 9")
progress_printer = ProgressPrinter("colorizeModel")
chunk.colorizeModel(source_data=Metashape.ImagesData,
                    progress=progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('buildUV', 'system.csv')
thread  = threading.Thread(target=monitor.start)
thread.start()

print("--Build Model UV 10")
progress_printer = ProgressPrinter("buildUV")
chunk.buildUV(mapping_mode=Metashape.GenericMapping,
              page_count = 1, texture_size = 8192,
              progress= progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

# Monitoring setup
monitor = SystemMonitor('buildTexture', 'system.csv')
thread  = threading.Thread(target=monitor.start)
thread.start()

print("--Build Texture 11")
progress_printer = ProgressPrinter("buildTexture")
chunk.buildTexture(
    blending_mode=Metashape.MosaicBlending,
    texture_size = 8192, 
    fill_holes=True,
    ghosting_filter = True,
    progress=progress_printer)
doc.save()

monitor.stop()
thread.join()   # wait thread end

# missing buildTiledModel
# missing detectMarkers

if has_transform:
    # Monitoring setup
    monitor = SystemMonitor('buildDem', 'system.csv')
    thread  = threading.Thread(target=monitor.start)
    thread.start()
    
    print("--Build DEM 12")
    progress_printer = ProgressPrinter("buildDem")
    chunk.buildDem(source_data=Metashape.PointCloudData,
                   interpolation= Metashape.EnabledInterpolation,
                   subdivide_task=True,
                   progress=progress_printer)
    # resolution(m)
    doc.save()

    monitor.stop()
    thread.join()   # wait thread end

    # Monitoring setup
    monitor = SystemMonitor('buildOrthomosaic', 'system.csv')
    thread  = threading.Thread(target=monitor.start)
    thread.start()

    print("--Build Orthomosaic 13")
    progress_printer = ProgressPrinter("buildOrthomosaic")
    chunk.buildOrthomosaic(surface_data=Metashape.ElevationData,
                           fill_holes= True,
                           subdivide_task=True,
                           progress= progress_printer)
    doc.save()

    monitor.stop()
    thread.join()   # wait thread end

# export results
chunk.exportReport(path=output_folder + '/report.pdf',
                   title="Report")

# missing exportCameras
# missing exportOrthophotos
# missing exportTexture
# missing exportTiledModel


if chunk.model:
    chunk.exportModel(output_folder + '/model.obj')

if chunk.point_cloud:
    chunk.exportPointCloud(output_folder + '/point_cloud.las', source_data = Metashape.PointCloudData)

if chunk.elevation:
    chunk.exportRaster(output_folder + '/dem.tif', source_data = Metashape.ElevationData)

if chunk.orthomosaic:
    chunk.exportRaster(output_folder + '/orthomosaic.tif', source_data = Metashape.OrthomosaicData)

print('Processing finished, results saved to ' + output_folder + '.')