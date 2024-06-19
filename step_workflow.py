# workflow_executor.py
import argparse
import json
import yaml
import os
from progress_printer import ProgressPrinter
from src.settings import Settings
from src.project import Project
from src.photoprocessor import PhotoProcessor


valid_steps = ['settings', 'project', 'PhotoProcessor']

"""
Core: esecuzione dei singoli steps scelti 
"""
def execute_steps(steps_params_to_run: dict):
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

    print("============SETTINGS===============")

    # Loading/New project
    if 'project' in steps_params_to_run:
        if not isinstance(steps_params_to_run['project']['path'], str) or not os.path.normpath(steps_params_to_run['project']['path']):
            raise ValueError("Error: specify a suitable path to project file")
        
        abs_path = "" 
        # check absolute/relative project path
        if os.path.isabs(steps_params_to_run['project']['path']):
            abs_path = steps_params_to_run['project']['path']
        else:
            abs_path = os.path.abspath(steps_params_to_run['project']['path'])
        
        print("è completo? ",abs_path)
        # path con file .psx o .psz
        if os.path.isfile(steps_params_to_run['project']['path']):
            _, extension = os.path.splitext(steps_params_to_run['project']['path'])
            if extension.lower() in ['.psx', '.psz']:
                print("è nel formato giusto ",abs_path)
                prj = Project(project_path=abs_path)
                prj.load_project()
            else:
                raise TypeError("Estenzione file non conforme a .psx/.psz di Metashape")
        else: 
        # new project file.psx
            # define name_project.psx
            prj = Project(project_path=abs_path.rstrip('/') + "/"+ os.path.basename(abs_path.rstrip('/')) +".psx")
            prj.new_project()

        """#TODO: DEBUGGING
        print("--DEGUB: lista di chunck ", prj.doc.chunks)
        print("--DEGUB: meta ", prj.doc.meta)
        print("--path: ", prj.doc.path)"""
    else:
        raise Exception("Non è stato specificato un save path o load project")
    """
    # TODO: commentare
    if 'PhotoProcessor' in steps_params_to_run:
        photoprocess = PhotoProcessor(photos_path=image_files)
        photoprocess.addPhotos(progress_printer=ProgressPrinter("addPhotos"))
    """

    
    # TODO: usare task https://www.agisoft.com/forum/index.php?topic=11428.msg51371#msg51371
        
    """
    # Ottieni il valore di un setting
    print(my_settings.get_setting('setting1'))  # Stampa 'value1'

    # Imposta il valore di un setting
    my_settings.set_setting('setting3', 'value3')
    """

    
"""
dato un json o yaml ritorna il dict {step: param}
"""
def get_config_from_file(filename: str) -> dict:
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                config = json.load(f)   # from json to dict
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                config = yaml.safe_load(f)  # from yaml to dict
            else:
                print(f"Errore: il file {filename} non è in un formato supportato. [YAML/JSON]")
                exit(1)
        return config['workflow']
    except FileNotFoundError:
        print(f"Errore: il file {filename} non è stato trovato.")
        exit(1)
    except (json.JSONDecodeError, yaml.YAMLError, EOFError):
        print(f"Errore: il file {filename} non è un file valido.")
        exit(1)

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

        # check output_folder exist
        if not os.path.isdir(output_save_folder):
            os.makedirs(output_save_folder, exist_ok=True)

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
