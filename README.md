[![DOI](https://www.openaccessrepository.it/badge/DOI/10.15161/oar.it/211632.svg)](https://doi.org/10.15161/oar.it/211632)

# UAV Photogrammetry Digital Twin Creation Scripts

This repository contains a collection of Python scripts for creating digital twins from UAV photogrammetry data. These scripts are derived from the examples provided in the [Agisoft Metashape](https://www.agisoft.com/) Scripts repository, which is licensed under the MIT License.

## Overview

The scripts provided here are tailored specifically for the creation of digital twins using UAV (Unmanned Aerial Vehicle) photogrammetry techniques. They offer functionalities for processing aerial imagery, generating 3D models, and creating digital representations of real-world environments.

## Usage

To use these scripts, you will need to have Agisoft Metashape Professional Edition installed on your system. Follow the instructions provided by Agisoft for installation and setup.

Once installed, simply clone this repository and run the scripts using Python. These scripts are not intended to be used inside the Metashape app GUI. Each script may require specific parameters to be set, so make sure to refer to the documentation provided with each script for detailed usage instructions.

It is possible to specify execution tasks by passing them as input or through a config file (YAML/JSON).
```bash
python step_workflow.py -i <path/to/folder/images> -c <config.json> -o [resulting/directory]
python step_workflow.py -i <path/to/folder/images> -e <"task1:param1 task2:param1,param2"> -o [resulting/directory]
```
It is possible to see all available commands with the following command
```bash
python step_workflow.py --help
```
To run the integrated unit test
```bash
python -m unittest
```

### Dependencies

This project requires some Python packages to run correctly. These packages are listed in the `requirements.txt` file included in this project.

To install these dependencies, run the following command:

```bash
pip install -r requirements.txt
```

#### Project layout
```bash
├── UAV-digital-twin  # Main folder
    ├── assets/        
        ├── Metashape-2.1.3....whl # Metashape Python module 2.1.3 (Linux, Mac, Win)
    ├── config.json   # E.g. configuration file to execute most of the steps
    ├── config.yaml   # E.g. configuration files to export data
    ├── demo/         # Folder containing demo code
        ├── demo_process.py     # Main demo code
    ├── docker        # Folder containing docker image
    ├── main.py       # Main code for running UAV-digital-twin v1.0 (full workflow)
    ├── reports       # Folder cointaing scripts for monitoring data analysis
        ├── report.ipynb    # Jupyter notebooks for running data analysis
        ├── report.py       # Python code for running data analysis
        ├── sample_data/
            ├── system.csv  # File of data sample   
    ├── step_workflow.py    # Main code for running UAV-digital-twin v1.1 (single task)
    ├── src/          # Folder code for UAV-digital-twin (UML in the doc)
    ├── requirements.txt    # Text file that lists all package dependencies required to run the project correctly
    ├── test/         # Folder containing code for unit tests
    ├── labelstudiorenamexport.py # Script renames label studio masks
```

## License

The scripts in this repository are distributed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

We would like to express our gratitude to Agisoft LLC for providing the examples that served as the foundation for these scripts.

This work is supported by Italian Research Center on High Performance Computing Big Data and Quantum Computing (ICSC), project funded by European Union - NextGenerationEU - and National Recovery and Resilience Plan (NRRP) - Mission 4 Component 2 within the activities of Spoke 3 (Astrophysics and Cosmos Observations
