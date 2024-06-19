# photoprocessor.py
import Metashape
from project import Project

"""
Esegue l'inserimento delle foto, il filtro qualità, il match delle foto e l'allineamento di queste per poi creare la nuvola sparsa di punti
"""

class PhotoProcessor:

    def __init__(self, photos_path: str = None) -> None:
        self.project = Project.get_project()
        self.photos_path = photos_path

    def addPhotos(self, progress_printer: str):
        self.project.chunk.addPhotos(filenames=self.photos_path,
                                     progress=progress_printer)
        self.project.save_project(version="addPhotos")
        print("-- "+ str(len(self.project.chunk.cameras)) + " images loaded")
    
    def filterImageQuality(self):
        num_disenable_photos = 0
        for camera in self.project.chunk.cameras:
            self.project.chunk.analyzePhotos(camera)
            if float(camera.photo.meta['Image/Quality']) < 0.5:
                camera.enabled = False
                num_disenable_photos += 1
        self.project.save_project(version="filterImageQuality")
        print("-- "+ str(len(self.project.chunk.cameras)- num_disenable_photos) + " images filtered")

    # TODO: optimize camera

    