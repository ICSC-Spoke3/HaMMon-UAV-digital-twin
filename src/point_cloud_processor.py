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

    """
    Build dense point cloud
    """
    def buildPointCloud(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'source_data': Metashape.DepthMapsData,
            'point_colors': True,
            'point_confidence': True,
            'keep_depth': True,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildPointCloud(progress=progress_printer, **default_params)
        self.project.save_project(version="buildPointCloud")

    """
    Calculate point colors for the point cloud
    """
    def colorizePointCloud(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'source_data': Metashape.ImagesData,
            'subdivide_task': True
        }
        print("--DEBUG: coloro")
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.colorizePointCloud(progress=progress_printer, **default_params)
        self.project.save_project(version="colorizePointCloud")


    



    