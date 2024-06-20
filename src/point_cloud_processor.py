# point_cloud_processor.py
from src.project import Project
import Metashape

"""
Determina il calcolo delle mappe di profondità dal quale sarà possibile determinare 
la nuvola densa di punti
"""

class PointCloudProcessor:

    def __init__(self) -> None:
        self.project = Project.get_project()

    """
    Build depth maps
    """
    def buildDepthMaps(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'downscale': 2,
            'filter_mode': Metashape.MildFiltering,
            'reuse_depth': False,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildDepthMaps(progress=progress_printer, **default_params)
        self.project.save_project(version="buildDepthMaps")

    



    