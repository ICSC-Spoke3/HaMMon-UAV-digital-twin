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
            self.project.chunk.exportRaster(path=path+"/dem.tif", progress= progress_printer, **default_params)

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
            self.project.chunk.exportRaster(path=path+"/orthomosaic.tif", progress= progress_printer, **default_params)

    # TODO: detect and filter point cloud confidence

    """
    Export Model
    """
    def exportModel(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.model:
            default_params = {
                "texture_format": Metashape.ImageFormat.ImageFormatTIFF,
                "save_texture": True,
                "save_uv": True,
                "save_normals": True,
                "save_colors": True,
                "save_confidence": True,
                "save_cameras": True,
                "save_markers": True,
                "embed_texture": True,
                "format": Metashape.ModelFormat.ModelFormatOBJ
            }
            # update default params with the input
            default_params.update(kwargs)
            self.project.chunk.exportModel(path=path+'/model.obj', progress= progress_printer, **default_params)

    """
    export dense point cloud
    """
    def exportPointCloud(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.point_cloud:
            default_params = {
                "source_data": Metashape.DataSource.PointCloudData,
                "save_point_color": True,
                #"save_point_normal": True, 
                #"save_point_intensity": True,
                #"save_point_classification": True, 
                #"save_point_confidence": True,
                #"save_point_source_id": True,
                #"save_point_index": True,
                #"format": Metashape.PointCloudFormat.PointCloudFormatLAS,
                        # format Metashape.PointCloudFormat.Cesium
                #"image_format": Metashape.ImageFormat.ImageFormatTIFF,
                #"split_in_blocks": False,
                            #"classes" (list[int]) – List of point classes to be exported,
                #"save_images": True,
                        # "compression": True,               
                        # "tileset_version": "1.1",
                        # "screen_space_error" (float) – Target screen space error (Cesium format only).
                        # "folder_depth" (int) – Tileset subdivision depth (Cesium format only)
                #"subdivide_task": True
            }
            # update default params with the input
            default_params.update(kwargs)
            self.project.chunk.exportPointCloud(path=path+'/point_cloud/point_cloud.las', progress=progress_printer,  **default_params)



