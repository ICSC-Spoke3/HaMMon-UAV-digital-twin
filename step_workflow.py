# workflow_executor.py
import argparse
import json
import yaml
import os
from src import step1
from src import step2


valid_steps = ['step1', 'step2', "step3"]

""" core """
def execute_steps(steps_params_to_run: dict):
    # check steps_params_to_run not empty
    if not steps_params_to_run:
        print("Errore: non ci sono processi da eseguire.")
        exit(1)
    # check steps_to_run are valid steps
    if any(step not in valid_steps for step in steps_params_to_run):
        print("Errore: uno o più processi specificati non sono validi.")
        exit(1)
        
    if 'step1' in steps_params_to_run:
        step1.run(steps_params_to_run['step1'])
    if 'step2' in steps_params_to_run:
        step2.run(steps_params_to_run['step2'])
    
"""
dato un json o yaml ritorna il dict {step: param}
"""
def get_config_from_file(filename: str) -> dict:
    try:
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                config = json.load(f)
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                config = yaml.safe_load(f)
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

""" In questo codice, prima divido l’input_config in base agli spazi, quindi per ogni elemento ottenuto, lo divido in base al carattere : per separare il nome del metodo dai parametri. Infine, divido i parametri in base alla virgola , per ottenere una lista di parametri."""
def get_config_from_cli(input_config: str)  -> dict:
    workflow = {}
    for config in input_config.split():
        step, params = config.split(':')
        workflow[step] = params.split(',')
    return workflow

"""Trova tutti i file con le estensioni specificate in una data cartella e ne ritorna la lista"""
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
    #TODO da gestire i folder di input e output
    input_images_folder = ""
    output_save_folder = "."
    
    args = parser.parse_args()
    # check input/output folder
    if args.input:
        input_images_folder = args.input

        # check image_folder exist
        if not os.path.isdir(input_images_folder):
            raise FileNotFoundError(f"{input_images_folder} does not exit")
        


    else:
        print("Error: Missing input photos folder. \nSpecifica <--input> il path delle raw photos.")
        exit(1)
    if args.output:
        output_save_folder = args.output
    # check config and exec parameters
    if args.config and args.exec:
        print("Errore: non puoi specificare sia <--config> che <--exec>.")
        exit(1)
    elif args.config:
        steps_params_to_run = get_config_from_file(args.config)
    elif args.exec:
        steps_params_to_run = get_config_from_cli(args.exec)
    else:
        print("Missing parameters. \nSpecifica <--config> per eseguire da un file di configurazione, o <--exec> per eseguire da linea di comando. \n<--help> per ulteriori informazioni.")
        exit(1)

    execute_steps(steps_params_to_run)
