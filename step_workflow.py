# workflow_executor.py
import argparse
import json
import yaml
import os
from src.progress_printer import ProgressPrinter
from src.settings import Settings
from src.project import Project
from src.photo_processor import PhotoProcessor
from src.point_cloud_processor import PointCloudProcessor
from src.mesh_processor import MeshProcessor
from src.geographic_projection import GeographicProjection


valid_steps = ['settings', 'project', 'PhotoProcessor', 'PointCloudProcessor', "3DModelProcessor", "OrthoAndDEMCreation", "exportResults"]

# return if any file.ext in path
def is_file_path(path) -> bool:
    return os.path.splitext(path)[1] != ''

"""
Core: esecuzione dei singoli steps scelti 
"""
def execute_steps(steps_params_to_run: dict) -> None:
    # check steps_params_to_run not empty
    if not steps_params_to_run:
        raise Exception("Errore: non ci sono processi da eseguire.")
    # check steps_to_run are valid steps
    if any(step not in valid_steps for step in steps_params_to_run):
        raise Exception("Errore: uno o più processi specificati non sono validi.")

    # Preferences
    if 'settings' in steps_params_to_run:
        my_settings = Settings(steps_params_to_run['settings'])
        if steps_params_to_run['settings']['log']:  # log
            my_settings.set_log(steps_params_to_run['settings']['log'])

        print("== == == == == SETTINGS == == == == ==")

    # Loading/New project
    if 'project' in steps_params_to_run:
        if not isinstance(steps_params_to_run['project']['path'], str) or not os.path.normpath(steps_params_to_run['project']['path']):
            raise ValueError("Error: specify a suitable path to project file")
        
        # set absolute project path
        abs_path = os.path.abspath(steps_params_to_run['project']['path'])
        
        # path con file .psx o .psz
        if is_file_path(steps_params_to_run['project']['path']):
            _, extension = os.path.splitext(steps_params_to_run['project']['path'])
            if extension.lower() in ['.psx', '.psz']:
                prj = Project(project_path=abs_path)
                prj.load_project()
            else:
                raise TypeError("Estenzione file non conforme a .psx/.psz di Metashape")
        else: 
        # define new project name_project.psx
            prj = Project(project_path=abs_path.rstrip('/') + "/"+ os.path.basename(abs_path.rstrip('/')) +".psx")
            prj.new_project()

        #print("--DEGUB: lista di chunck ", prj.doc.chunks)
        #print("--DEGUB: meta ", prj.doc.meta)
        #print("--path: ", prj.doc.path)
        print(" == == == Loading/NewProject == == ==")
    else:
        raise Exception("Non è stato specificato un save path o load project")

    if 'PhotoProcessor' in steps_params_to_run:
        photoprocess = PhotoProcessor(photos_path=image_files)
        photoprocess.addPhotos(progress_printer=ProgressPrinter("addPhotos"))
        photoprocess.filterImageQuality(progress_printer=ProgressPrinter("filterPhotos"))
        if 'matchPhotos' in steps_params_to_run['PhotoProcessor']:
            photoprocess.matchPhotos(progress_printer=ProgressPrinter("matchPhotos"), **steps_params_to_run['PhotoProcessor']['matchPhotos'])
        else: # do it by default
            photoprocess.matchPhotos(progress_printer=ProgressPrinter("matchPhotos"))
        if 'alignCameras' in steps_params_to_run['PhotoProcessor']:
            photoprocess.alignCameras(progress_printer=ProgressPrinter("alignCameras"), **steps_params_to_run['PhotoProcessor']['alignCameras'])
        else: # do it by default
            photoprocess.alignCameras(progress_printer=ProgressPrinter("alignCameras"))
        if 'optimizeCameras' in steps_params_to_run['PhotoProcessor']:
            photoprocess.optimizeCameras(progress_printer=ProgressPrinter("optimizeCameras"), **steps_params_to_run['PhotoProcessor']['optimizeCameras'])
    
        print(" == == == Loading/NewProject == == ==")

    if 'PointCloudProcessor' in steps_params_to_run:
        pointcloudprocess = PointCloudProcessor()
        if 'buildDepthMaps' in steps_params_to_run['PointCloudProcessor']:
            pointcloudprocess.buildDepthMaps(progress_printer=ProgressPrinter("buildDepthMaps"), **steps_params_to_run['PointCloudProcessor']['buildDepthMaps'])
        else: # do it by default
            pointcloudprocess.buildDepthMaps(progress_printer=ProgressPrinter("buildDepthMaps"))

        """
        check chunk location in the world coordinate system: scale component, rotation component, translation component
        """
        if (pointcloudprocess.project.chunk.transform.scale and 
            pointcloudprocess.project.chunk.transform.rotation and 
            pointcloudprocess.project.chunk.transform.translation):
            if 'buildPointCloud' in steps_params_to_run['PointCloudProcessor']:
                pointcloudprocess.buildPointCloud(progress_printer=ProgressPrinter("buildPointCloud"), **steps_params_to_run['PointCloudProcessor']['buildPointCloud'])
            else:
                pointcloudprocess.buildPointCloud(progress_printer=ProgressPrinter("buildPointCloud"))
            pointcloudprocess.colorizePointCloud(progress_printer=ProgressPrinter("colorizePointCloud"))
            if 'exportPointCloud' in steps_params_to_run['PointCloudProcessor']:
                pointcloudprocess.exportPointCloud(progress_printer=ProgressPrinter("exportPointCloud"), path=output_save_folder,  **steps_params_to_run['PointCloudProcessor']['exportPointCloud'])

        print(" == == == PointCloudProcessor == == ==")

    if "3DModelProcessor" in steps_params_to_run:
        meshprocess = MeshProcessor()
        if 'buildModel' in steps_params_to_run['3DModelProcessor']:
            meshprocess.buildModel(progress_printer=ProgressPrinter("buildModel"), **steps_params_to_run['3DModelProcessor']['buildModel'])
        else: # do it by default
            meshprocess.buildModel(progress_printer=ProgressPrinter("buildModel"))
        meshprocess.colorizeModel(progress_printer=ProgressPrinter("colorizeModel"))
        if 'buildUV' in steps_params_to_run['3DModelProcessor']:
            meshprocess.buildUV(progress_printer=ProgressPrinter("buildUV"), **steps_params_to_run['3DModelProcessor']['buildUV'])
        else: # do it by default
            meshprocess.buildUV(progress_printer=ProgressPrinter("buildUV"))
        if 'buildTexture' in steps_params_to_run['3DModelProcessor']:
            meshprocess.buildTexture(progress_printer=ProgressPrinter("buildTexture"), **steps_params_to_run['3DModelProcessor']['buildTexture'])
        else: # do it by default
            meshprocess.buildTexture(progress_printer=ProgressPrinter("buildTexture"))
        if 'buildTiledModel' in steps_params_to_run['3DModelProcessor']:
            meshprocess.buildTiledModel(progress_printer=ProgressPrinter("buildTiledModel"), **steps_params_to_run['3DModelProcessor']['buildTiledModel'])
        else: # do it by default
            meshprocess.buildTiledModel(progress_printer=ProgressPrinter("buildTiledModel"))

        print(" == == == 3DModelProcessor == == ==")

    if "OrthoAndDEMCreation" in steps_params_to_run:
        orthodemprocess = GeographicProjection()
        if (orthodemprocess.project.chunk.transform.scale and 
            orthodemprocess.project.chunk.transform.rotation and 
            orthodemprocess.project.chunk.transform.translation):
            if 'buildDem' in steps_params_to_run['OrthoAndDEMCreation']:
                orthodemprocess.buildDem(progress_printer=ProgressPrinter("buildDem"))
                if 'exportDEM' in steps_params_to_run['OrthoAndDEMCreation']:
                    orthodemprocess.exportDEM(progress_printer=ProgressPrinter("exportDEM"), path=output_save_folder, **steps_params_to_run['OrthoAndDEMCreation']['exportDEM'])
            if 'buildOrtho' in steps_params_to_run['OrthoAndDEMCreation']:
                orthodemprocess.buildOrthomosaic(progress_printer=ProgressPrinter("buildOrtho"))
                if 'exportOrtho' in steps_params_to_run['OrthoAndDEMCreation']:
                    orthodemprocess.exportOrtho(progress_printer=ProgressPrinter("exportOrtho"), path=output_save_folder,  **steps_params_to_run['OrthoAndDEMCreation']['exportOrtho'])


    if 'exportResults' in steps_params_to_run:
        orthodemprocess = GeographicProjection()
        meshprocess = MeshProcessor()
        if 'exportDEM' in steps_params_to_run['exportResults']:
            orthodemprocess.exportDEM(progress_printer=ProgressPrinter("exportDEM"), path=output_save_folder, **steps_params_to_run['exportResults']['exportDEM'])
        if 'exportOrtho' in steps_params_to_run['exportResults']:
            orthodemprocess.exportOrtho(progress_printer=ProgressPrinter("exportOrtho"), path=output_save_folder,  **steps_params_to_run['exportResults']['exportOrtho'])
        if 'exportModel' in steps_params_to_run['exportResults']:
            meshprocess.exportModel(progress_printer=ProgressPrinter("exportModel"), path=output_save_folder,  **steps_params_to_run['exportResults']['exportModel'])
        if 'exportPointCloud' in steps_params_to_run['exportResults']:
                orthodemprocess.exportPointCloud(progress_printer=ProgressPrinter("exportPointCloud"), path=output_save_folder,  **steps_params_to_run['exportResults']['exportPointCloud'])

# TODO: export tiled model
    # TODO: fix export in concomitanza della creazione del modello
                #TODO fix if and else annidato non annidato, visto che posso esportarlo a piacere, con le casistiche che voglio io
    # TODO: usare task https://www.agisoft.com/forum/index.php?topic=11428.msg51371#msg51371

    prj.chunk.exportReport(path="./report.pdf", title="Final report")

    
"""
dato un json o yaml ritorna il dict={step: param}
"""
def get_config_from_file(filename: str) -> dict:
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                config = json.load(f)   # from json to dict
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                config = yaml.safe_load(f)  # from yaml to dict
            else:
                raise PermissionError(f"Errore: il file {filename} non è in un formato supportato. [YAML/JSON]")
        return config['workflow']
    except FileNotFoundError:
        raise FileNotFoundError(f"Errore: il file {filename} non è stato trovato.")
    except (json.JSONDecodeError, yaml.YAMLError, EOFError):
        raise PermissionError(f"Errore: il file {filename} non è un file valido.")


"""
Estrapolo i parametri presi in input a partire dalla command line
Divido l’input_config in base agli spazi, quindi per ogni elemento ottenuto, lo divido in base al carattere: per separare il nome del metodo dai parametri. 
Infine, divido i parametri in base alla virgola, per ottenere una lista di parametri.
"""
def get_config_from_cli(input_config: str)  -> dict:
    workflow = {}
    for config in input_config.split():
        step, params = config.split(':')
        workflow[step] = params.split(',')
    return workflow

""" 
Trova tutti i file con le estensioni specificate in una data cartella e ne ritorna la lista 
"""
def find_files(folder: str, types: list[str]) -> list[str]:
    files = []
    for entry in os.scandir(folder):
        if entry.is_file():
            file_extension = os.path.splitext(entry.name)[1].lower()
            if file_extension in types:
                files.append(entry.path)
    return files

if __name__ == "__main__":
    # args argument
    parser = argparse.ArgumentParser(description='Esegue il workflow degli specificati step del processo fotogrammetrico.')
    parser.add_argument('-e', '--exec', help='Specifica gli step di esecuzione e i parametri richiesti da linea di comando (es. "step1:ciao1,ciao2 step2:ciao3"')
    parser.add_argument('-c', '--config', help='Path configuration file JSON/YAML')
    parser.add_argument('-i', '--input', help='Path project photos')
    parser.add_argument('-o', '--output', help='Saving path project files')
    parser.add_argument('-p', '--project', help='Save/Open project path name')

    #TODO: integrare -p negli obligatori e nei CLI
    
    input_images_folder = ""
    output_save_folder = "."
    
    args = parser.parse_args()
    # check input folder
    if args.input:
        input_images_folder = args.input

        # check image_folder exist
        if not os.path.isdir(input_images_folder):
            raise FileNotFoundError(f"{input_images_folder} does not exit")
        
        # check number of images    # TODO lista delle estensioni da aggiornare
        image_files = find_files(input_images_folder, [".jpg", ".jpeg", ".tif", ".tiff", ".png", ".bmp", ".dng"])
        if len(image_files) < 2:
            raise ValueError("Not enough images to process in the path.")
    else:
        raise Exception("Missing input photos folder. Specifica:\n <--input> il path delle raw photos.")

    # check output folder
    if args.output:
        output_save_folder = args.output

        # check output_folder exist and every subfolder
        if not os.path.isdir(output_save_folder):
            os.makedirs(output_save_folder, exist_ok=True)
        if not os.path.isdir(output_save_folder+ "/point_cloud/"):
            os.makedirs(output_save_folder+ "/point_cloud/", exist_ok=True)

    # check config and exec parameters
    if args.config and args.exec:
        raise Exception("Error: you cannot specify both <–config> and <–exec>.")
    elif args.config:
        steps_params_to_run = get_config_from_file(args.config)
    elif args.exec:
        steps_params_to_run = get_config_from_cli(args.exec)
    else:
        raise Exception("Missing parameters. Specify \n<–config> to run from a configuration file, or <–exec> to run from the command line. \n<–output> saving project path \n<–help> for more information.")

    execute_steps(steps_params_to_run)
