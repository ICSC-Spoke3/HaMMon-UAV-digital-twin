# mesh_processor.py
from src.project import Project
import Metashape

"""
Determina la creazione della mesh del modello, la texture a partire dalle foto e il tiled model
"""

class MeshProcessor:

    def __init__(self) -> None:
        self.project = Project.get_project()

    """
    Build 3D model 
    """
    def buildModel(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'surface_type': Metashape.Arbitrary,
            'source_data': Metashape.DepthMapsData,
            'interpolation': Metashape.EnabledInterpolation,
            'face_count': Metashape.HighFaceCount,
            'vertex_colors': True,
            'vertex_confidence': True,
            'keep_depth': True,
            'build_texture': True,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildModel(progress=progress_printer, **default_params)
        self.project.save_project(version="buildModel")

    """
    Colorize 3D model
    """
    def colorizeModel(self, progress_printer: str) -> None:
        self.project.chunk.colorizeModel(source_data=Metashape.ImagesData, progress=progress_printer)
        print("--FUNZIONA?????????????")
        self.project.save_project(version="colorizeModel")


