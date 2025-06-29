"""
export all worker information

How to use:
python export_worker_info.py
"""

import Metashape
import os
import json

client = Metashape.NetworkClient()
client.connect(os.getenv("METASHAPE_SERVER"))

# Loop through the workers and get the worker_id
for worker in client.workerList()['workers']:
    worker_id = worker['worker_id']
    file_name = f'worker_{worker_id}.json'
    worker_info = client.workerInfo(worker_id)
    with open(file_name, 'w') as json_file:
        json.dump(worker_info, json_file, indent=4)

