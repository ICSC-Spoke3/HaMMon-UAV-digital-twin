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
    Export Digital Elevation Model
    """
    def exportDEM(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.elevation:
            default_params = {
                "image_format": Metashape.ImageFormatTIFF,
                "source_data": Metashape.ElevationData
            }
            # update default params with the input
            default_params.update(kwargs)
            self.project.chunk.exportRaster(path=path+"/dem/dem.tif", progress= progress_printer, **default_params)

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

    """
    Export Orthomosaic
    """
    def exportOrtho(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.orthomosaic:
            default_params = {
                "image_format": Metashape.ImageFormatTIFF,
                "source_data": Metashape.OrthomosaicData,
                "split_in_blocks": True
            }
            # update default params with the input
            default_params.update(kwargs)
            self.project.chunk.exportRaster(path=path+"/orthomosaic/orthomosaic.tif", progress= progress_printer, **default_params)
            
