# mesh_processor.py
from src.project import Project
import Metashape
import threading

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
        self.project.chunk.colorizeModel(source_data=Metashape.ImagesData, progress=progress_printer)
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
        self.project.chunk.buildUV(progress=progress_printer, **default_params)
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
        self.project.chunk.buildTexture(progress=progress_printer, **default_params)
        self.project.save_project(version="buildTexture")

    # TODO: detectMarkers
        
    # buildTiledModel: https://www.agisoft.com/forum/index.php?topic=13206.0
    """
    Build tiled model
    """
    def buildTiledModel(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'pixel_size': 0,
            'tile_size': 256,
            'source_data': Metashape.DataSource.DepthMapsData,
            'face_count': 20000,
            'ghosting_filter': False,
            'transfer_texture': False,
            'keep_depth': True,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        self.project.chunk.buildTiledModel(progress=progress_printer, **default_params)
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
            self.project.chunk.exportModel(path=path+'/model/model.obj', progress= progress_printer, **default_params)

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
            self.project.chunk.exportTiledModel(path=path+'/tiled/tiled.zip', progress= progress_printer, **default_params)

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
            self.project.chunk.exportTexture(path=path+'/texture/texture.jpg', progress= progress_printer, **default_params)    # png o tiff
