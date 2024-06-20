# photoprocessor.py
import Metashape
from src.project import Project

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
    
    """
    Estimate the image quality. Cameras with a quality less than 0.5 are considered blurred and it’s recommended to disable them.
    """
    def filterImageQuality(self, progress_printer: str):
        num_disable_photos = 0
        for camera in self.project.chunk.cameras:
            self.project.chunk.analyzeImages(camera)
            if float(camera.photo.meta['Image/Quality']) < 0.5:
                camera.enabled = False
                num_disable_photos += 1
        print("-- "+ str(len(self.project.chunk.cameras)- num_disable_photos) + " images filtered")
        self.project.save_project(version="filterImageQuality")

    def filterNuovo(self, progress_printer: str):
        self.project.chunk.analyzeImages(cameras=self.project.chunk.cameras, progress=progress_printer)
        print()
        print(self.project.chunk.cameras[0].meta.keys(), 
              self.project.chunk.cameras[0].meta.values())
        for camera in self.project.chunk.cameras:
            print(camera.photo.meta['Image/Quality'])
        """
        num_disable_photos = 0
        for camera in self.project.chunk.cameras:
            if float(camera.photo.meta['Image/Quality']) < 0.5:
                camera.enabled = False
                num_disable_photos += 1
        print("-- "+ str(len(self.project.chunk.cameras)- num_disable_photos) + " images filtered")
        self.project.save_project(version="filterImageQuality")
        """
        

    # TODO: optimize camera

    