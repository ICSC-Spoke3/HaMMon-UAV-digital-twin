# geographic_projection.py
from src.project import Project
import Metashape

"""
Determina la creazione dell'orthomosaico e del DEM
"""

class GeographicProjection:

    def __init__(self) -> None:
        self.project = Project.get_project()

    """
    Build Digital Elevation Model
    """
    def buildDem(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'source_data': Metashape.PointCloudData,
            'interpolation': Metashape.EnabledInterpolation,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildDem(progress=progress_printer, **default_params)
        self.project.save_project(version="buildDem")

    """
    Build Orthomosaic
    """
    def buildOrthomosaic(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'surface_data': Metashape.ElevationData,
            'fill_holes': True,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildOrthomosaic(progress=progress_printer, **default_params)
        self.project.save_project(version="buildOrthomosaic")

