# mesh_processor.py
from src.project import Project
import Metashape
import threading

"""
Determina la creazione della mesh del modello, la texture a partire dalle foto e il tiled model
"""

filter_modes = {
    "Metashape.SurfaceType.Arbitrary": Metashape.SurfaceType.Arbitrary,
    "Metashape.Arbitrary": Metashape.SurfaceType.Arbitrary,
    "Metashape.SurfaceType.HeightField": Metashape.SurfaceType.HeightField,
    "Metashape.HeightField": Metashape.SurfaceType.HeightField,
    "Metashape.Interpolation.DisabledInterpolation": Metashape.Interpolation.DisabledInterpolation,
    "Metashape.DisabledInterpolation": Metashape.Interpolation.DisabledInterpolation,
    "Metashape.Interpolation.EnabledInterpolation": Metashape.Interpolation.EnabledInterpolation,
    "Metashape.EnabledInterpolation": Metashape.Interpolation.EnabledInterpolation,
    "Metashape.Interpolation.Extrapolated": Metashape.Interpolation.Extrapolated,
    "Metashape.Extrapolated": Metashape.Interpolation.Extrapolated,
    "Metashape.FaceCount.LowFaceCount": Metashape.FaceCount.LowFaceCount,
    "Metashape.LowFaceCount": Metashape.FaceCount.LowFaceCount,
    "Metashape.FaceCount.MediumFaceCount": Metashape.FaceCount.MediumFaceCount,
    "Metashape.MediumFaceCount": Metashape.FaceCount.MediumFaceCount,
    "Metashape.FaceCount.HighFaceCount": Metashape.FaceCount.HighFaceCount,
    "Metashape.HighFaceCount": Metashape.FaceCount.HighFaceCount,
    "Metashape.FaceCount.CustomFaceCount": Metashape.FaceCount.CustomFaceCount,
    "Metashape.CustomFaceCount": Metashape.FaceCount.CustomFaceCount,
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
    "Metashape.MappingMode.GenericMapping": Metashape.MappingMode.GenericMapping,
    "Metashape.GenericMapping": Metashape.MappingMode.GenericMapping,
    "Metashape.MappingMode.OrthophotoMapping": Metashape.MappingMode.OrthophotoMapping,
    "Metashape.OrthophotoMapping": Metashape.MappingMode.OrthophotoMapping,
    "Metashape.MappingMode.AdaptiveOrthophotoMapping": Metashape.MappingMode.AdaptiveOrthophotoMapping,
    "Metashape.AdaptiveOrthophotoMapping": Metashape.MappingMode.AdaptiveOrthophotoMapping,
    "Metashape.MappingMode.SphericalMapping": Metashape.MappingMode.SphericalMapping,
    "Metashape.SphericalMapping": Metashape.MappingMode.SphericalMapping,
    "Metashape.MappingMode.CameraMapping": Metashape.MappingMode.CameraMapping,
    "Metashape.CameraMapping": Metashape.MappingMode.CameraMapping,
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
            'split_in_blocks': False,
            'blocks_size': 250,
            'build_texture': True,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        if 'surface_type' in kwargs:
            try:
                surface_type = filter_modes.get(kwargs['surface_type'], Metashape.Arbitrary)
            except AttributeError:
                print(f"Note: '{kwargs['surface_type']}' is not valid on Metashape.")
            default_params['surface_type'] = surface_type  # surface_type updated correctly
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.DepthMapsData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly
        if 'interpolation' in kwargs:
            try:
                interpolation = filter_modes.get(kwargs['interpolation'], Metashape.EnabledInterpolation)
            except AttributeError:
                print(f"Note: '{kwargs['interpolation']}' is not valid on Metashape.")
            default_params['interpolation'] = interpolation  # interpolation updated correctly
        if 'face_count' in kwargs:
            try:
                face_count = filter_modes.get(kwargs['face_count'], Metashape.HighFaceCount)
            except AttributeError:
                print(f"Note: '{kwargs['face_count']}' is not valid on Metashape.")
            default_params['face_count'] = face_count  # face_count updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildModel',))
            thread.start()
        self.project.chunk.buildModel(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildModel")

    """
    Colorize 3D model
    """
    def colorizeModel(self, progress_printer: str) -> None:
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('colorizeModel',))
            thread.start()
        self.project.chunk.colorizeModel(source_data=Metashape.ImagesData, progress=progress_printer)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="colorizeModel")

    """
    Generate uv mapping for the model
    """
    def buildUV(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'mapping_mode': Metashape.GenericMapping,
            'page_count': 1,
            'texture_size': 8192
        }
        # update default params with the input
        default_params.update(kwargs)
        if 'mapping_mode' in kwargs:
            try:
                mapping_mode = filter_modes.get(kwargs['mapping_mode'], Metashape.GenericMapping)
            except AttributeError:
                print(f"Note: '{kwargs['mapping_mode']}' is not valid on Metashape.")
            default_params['mapping_mode'] = mapping_mode  # mapping_mode updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildUV',))
            thread.start()
        self.project.chunk.buildUV(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildUV")

    """
    Generate texture layer
    """
    def buildTexture(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'blending_mode': Metashape.MosaicBlending,
            'texture_size': 8192,
            'fill_holes': True,
            'ghosting_filter': True
        }
        # update default params with the input
        default_params.update(kwargs)
        if 'blending_mode' in kwargs:
            try:
                blending_mode = filter_modes.get(kwargs['blending_mode'], Metashape.MosaicBlending)
            except AttributeError:
                print(f"Note: '{kwargs['blending_mode']}' is not valid on Metashape.")
            default_params['blending_mode'] = blending_mode  # blending_mode updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildTexture',))
            thread.start()
        self.project.chunk.buildTexture(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildTexture")

        
    # buildTiledModel: https://www.agisoft.com/forum/index.php?topic=13206.0
    """
    Build tiled model
    """
    def buildTiledModel(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'pixel_size': 0,
            'tile_size': 256,
            'source_data': Metashape.DataSource.PointCloudData,
            'face_count': 20000,
            'ghosting_filter': False,
            'transfer_texture': False,
            'keep_depth': True,
            'subdivide_task': True
        }
        #TODO: source_data: Selects between point cloud and mesh.
        # update default params with the input
        default_params.update(kwargs)
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.PointCloudData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildTiledModel',))
            thread.start()
        self.project.chunk.buildTiledModel(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildTiledModel")

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
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportModel',))
                thread.start()
            self.project.chunk.exportModel(path=path+'/model/model.obj', progress= progress_printer, **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()

    """
    Export TiledModel
    """
    def exportTiledModel(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.tiled_model:
            default_params = {
                "format": Metashape.TiledModelFormat.TiledModelFormatCesium,
                "model_format" : Metashape.ModelFormat.ModelFormatCOLLADA,
                "texture_format": Metashape.ImageFormat.ImageFormatJPEG,
                "model_compression": True,
                "tileset_version": '1.1',
                "use_tileset_transform": True,
                "folder_depth": 5
            }
            # update default params with the input
            default_params.update(kwargs)
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportTiledModel',))
                thread.start()
            self.project.chunk.exportTiledModel(path=path+'/tiled/tiled.zip', progress= progress_printer, **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()

    """
    Export model texture to file
    """
    def exportTexture(self, progress_printer: str, path: str, **kwargs):
        if self.project.chunk.model.textures:
            default_params = {
                "texture_type":  Metashape.Model.TextureType.DiffuseMap,
                "raster_transform": Metashape.RasterTransformType.RasterTransformNone,
                "save_alpha": False
            }
            default_params.update(kwargs)
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportTexture',))
                thread.start()
            self.project.chunk.exportTexture(path=path+'/texture/texture.jpg', progress= progress_printer, **default_params)    # png/tiff
            if self.project.monitoring is not None:
                self.project.monitoring.stop()
