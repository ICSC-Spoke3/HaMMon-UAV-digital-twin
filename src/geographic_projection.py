# geographic_projection.py
from src.project import Project
import Metashape
import threading


filter_modes = {
    "Metashape.DataSource.TiePointsData": Metashape.DataSource.TiePointsData,
    "Metashape.TiePointsData": Metashape.DataSource.TiePointsData,
    "Metashape.DataSource.PointCloudData": Metashape.DataSource.PointCloudData,
    "Metashape.PointCloudData": Metashape.DataSource.PointCloudData,
    "Metashape.DataSource.ModelData": Metashape.DataSource.ModelData,
    "Metashape.ModelData": Metashape.DataSource.ModelData,
    "Metashape.DataSource.TiledModelData": Metashape.DataSource.TiledModelData,
    "Metashape.TiledModelData": Metashape.DataSource.TiledModelData,
    "Metashape.DataSource.ElevationData": Metashape.DataSource.ElevationData,
    "Metashape.ElevationData": Metashape.DataSource.ElevationData,
    "Metashape.DataSource.OrthomosaicData": Metashape.DataSource.OrthomosaicData,
    "Metashape.OrthomosaicData": Metashape.DataSource.OrthomosaicData,
    "Metashape.DataSource.DepthMapsData": Metashape.DataSource.DepthMapsData,
    "Metashape.DepthMapsData": Metashape.DataSource.DepthMapsData,
    "Metashape.DataSource.ImagesData": Metashape.DataSource.ImagesData,
    "Metashape.ImagesData": Metashape.DataSource.ImagesData,
    "Metashape.DataSource.TrajectoryData": Metashape.DataSource.TrajectoryData,
    "Metashape.TrajectoryData": Metashape.DataSource.TrajectoryData,
    "Metashape.DataSource.LaserScansData": Metashape.DataSource.LaserScansData,
    "Metashape.LaserScansData": Metashape.DataSource.LaserScansData,
    "Metashape.DataSource.DepthMapsAndLaserScansData": Metashape.DataSource.DepthMapsAndLaserScansData,
    "Metashape.DepthMapsAndLaserScansData": Metashape.DataSource.DepthMapsAndLaserScansData,
    "Metashape.Interpolation.DisabledInterpolation": Metashape.Interpolation.DisabledInterpolation,
    "Metashape.DisabledInterpolation": Metashape.Interpolation.DisabledInterpolation,
    "Metashape.Interpolation.EnabledInterpolation": Metashape.Interpolation.EnabledInterpolation,
    "Metashape.EnabledInterpolation": Metashape.Interpolation.EnabledInterpolation,
    "Metashape.Interpolation.Extrapolated": Metashape.Interpolation.Extrapolated,
    "Metashape.Extrapolated": Metashape.Interpolation.Extrapolated,
    "Metashape.BlendingMode.AverageBlending": Metashape.BlendingMode.AverageBlending,
    "Metashape.AverageBlending": Metashape.BlendingMode.AverageBlending,
    "Metashape.BlendingMode.MosaicBlending": Metashape.BlendingMode.MosaicBlending,
    "Metashape.MosaicBlending": Metashape.BlendingMode.MosaicBlending,
    "Metashape.BlendingMode.MinBlending": Metashape.BlendingMode.MinBlending,
    "Metashape.MinBlending": Metashape.BlendingMode.MinBlending,
    "Metashape.BlendingMode.MaxBlending": Metashape.BlendingMode.MaxBlending,
    "Metashape.MaxBlending": Metashape.BlendingMode.MaxBlending,
    "Metashape.BlendingMode.DisabledBlending": Metashape.BlendingMode.DisabledBlending,
    "Metashape.DisabledBlending": Metashape.BlendingMode.DisabledBlending
}
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
        # TODO: source_data: Selects between point cloud and tie points.
        # update default params with the input
        default_params.update(kwargs)
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.PointCloudData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly
        if 'interpolation' in kwargs:
            try:
                interpolation = filter_modes.get(kwargs['interpolation'], Metashape.EnabledInterpolation)
            except AttributeError:
                print(f"Note: '{kwargs['interpolation']}' is not valid on Metashape.")
            default_params['interpolation'] = interpolation  # interpolation updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildDem',))
            thread.start()
        self.project.chunk.buildDem(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
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
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportDEM',))
                thread.start()
            self.project.chunk.exportRaster(path=path+"/dem/dem.tif", progress= progress_printer, **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()

    """
    Build Orthomosaic
    """
    def buildOrthomosaic(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'surface_data': Metashape.ElevationData,
            'fill_holes': True,
            'subdivide_task': True,
            'blending_mode': Metashape.MosaicBlending
        }
        # update default params with the input
        default_params.update(kwargs)
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.PointCloudData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly
        if 'blending_mode' in kwargs:
            try:
                blending_mode = filter_modes.get(kwargs['blending_mode'], Metashape.MosaicBlending)
            except AttributeError:
                print(f"Note: '{kwargs['blending_mode']}' is not valid on Metashape.")
            default_params['blending_mode'] = blending_mode  # blending_mode updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildOrthomosaic',))
            thread.start()
        self.project.chunk.buildOrthomosaic(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildOrthomosaic")

    """
    Export Orthomosaic
    """
    def exportOrthomosaic(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.orthomosaic:
            default_params = {
                "image_format": Metashape.ImageFormatTIFF,
                "source_data": Metashape.OrthomosaicData,
                "split_in_blocks": True
            }
            # update default params with the input
            default_params.update(kwargs)
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportOrthomosaic',))
                thread.start()
            self.project.chunk.exportRaster(path=path+"/orthomosaic/orthomosaic.tif", progress= progress_printer, **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()

    """
    Export Orthophoto
    """
    def exportOrthophotos(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.orthomosaic:
            default_params = {
                "raster_transform": Metashape.RasterTransformType.RasterTransformNone,
                "resolution": 0,
                "resolution_x": 0,
                "resolution_y": 0,
                "save_kml": False,
                "save_world": False,
                "save_alpha": True,
                "image_compression": Metashape.ImageCompression.TiffCompressionJPEG,
                "white_background": True, 
                "north_up": True
            }
            # update default params with the input
            default_params.update(kwargs)
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportOrthophotos',))
                thread.start()
            self.project.chunk.exportOrthophotos(path=path+"/orthophotos/orthophoto.tif", progress= progress_printer, **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()           
