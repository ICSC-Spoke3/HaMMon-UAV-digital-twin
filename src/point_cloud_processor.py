# point_cloud_processor.py
from src.project import Project
import Metashape
import threading


filter_modes = {
    "Metashape.FilterMode.MildFiltering": Metashape.FilterMode.MildFiltering,
    "Metashape.MildFiltering": Metashape.FilterMode.MildFiltering,
    "Metashape.FilterMode.NoFiltering": Metashape.FilterMode.NoFiltering,
    "Metashape.NoFiltering": Metashape.FilterMode.NoFiltering,
    "Metashape.FilterMode.ModerateFiltering": Metashape.FilterMode.ModerateFiltering,
    "Metashape.ModerateFiltering": Metashape.FilterMode.ModerateFiltering,
    "Metashape.FilterMode.AggressiveFiltering": Metashape.FilterMode.AggressiveFiltering,
    "Metashape.AggressiveFiltering": Metashape.FilterMode.AggressiveFiltering,
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
    "Metashape.DepthMapsAndLaserScansData": Metashape.DataSource.DepthMapsAndLaserScansData
}

def update_existing_keys(dict1, dict2):
    for k in dict1.keys():
        if k in dict2:
            dict1[k] = dict2[k]
    return dict1

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
            'filter_mode': Metashape.FilterMode.MildFiltering,
            'reuse_depth': False,
            'subdivide_task': True
        }
        # update default params with the input
        # default_params.update(kwargs)
        default_params = update_existing_keys(default_params, kwargs)
        # update default params with the filter_mode if exist
        if 'filter_mode' in kwargs:
            try:
                filter_mode = filter_modes.get(kwargs['filter_mode'], Metashape.MildFiltering)
            except AttributeError:
                print(f"Note: '{kwargs['filter_mode']}' is not valid on Metashape.")
            default_params['filter_mode'] = filter_mode  # filter_mode updated correctly
            
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildDepthMaps',))
            thread.start()
        self.project.chunk.buildDepthMaps(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
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
        #default_params.update(kwargs)
        default_params = update_existing_keys(default_params, kwargs)
        # update default params with the source_data if exist
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.DepthMapsData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly
        
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('buildPointCloud',))
            thread.start()
        self.project.chunk.buildPointCloud(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="buildPointCloud")


    """
    Calculate point colors for the point cloud
    """
    def colorizePointCloud(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'source_data': Metashape.ImagesData,
            'subdivide_task': True
        }

        # update default params with the input
        #default_params.update(kwargs)
        default_params = update_existing_keys(default_params, kwargs)
        if 'source_data' in kwargs:
            try:
                source_data = filter_modes.get(kwargs['source_data'], Metashape.ImagesData)
            except AttributeError:
                print(f"Note: '{kwargs['source_data']}' is not valid on Metashape.")
            default_params['source_data'] = source_data  # source_data updated correctly

        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('colorizePointCloud',))
            thread.start()
        self.project.chunk.colorizePointCloud(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="colorizePointCloud")

        
    """
    export dense point cloud
    """
    def exportPointCloud(self, progress_printer: str, path: str, **kwargs) -> None:
        if self.project.chunk.point_cloud:
            default_params = {
                "source_data": Metashape.DataSource.PointCloudData,
                "save_point_color": True,
                "save_point_normal": True, 
                "save_point_intensity": True,
                "save_point_classification": True, 
                "save_point_confidence": True,
                "save_point_source_id": True,
                "save_point_index": True,
                "format": Metashape.PointCloudFormat.PointCloudFormatLAS,
                        # format Metashape.PointCloudFormat.Cesium
                "image_format": Metashape.ImageFormat.ImageFormatTIFF,
                "split_in_blocks": False,
                            #"classes" (list[int]) – List of point classes to be exported,
                #"save_images": True,
                        # "compression": True,               
                        # "tileset_version": "1.1",
                        # "screen_space_error" (float) – Target screen space error (Cesium format only).
                        # "folder_depth" (int) – Tileset subdivision depth (Cesium format only)
                "subdivide_task": True
            }
            # update default params with the input
            #default_params.update(kwargs)
            default_params = update_existing_keys(default_params, kwargs)
            if self.project.monitoring is not None:
                thread = threading.Thread(target=self.project.monitoring.start, args=('exportPointCloud',))
                thread.start()
            self.project.chunk.exportPointCloud(path=path+'/point_cloud/point_cloud.las', progress=progress_printer,  **default_params)
            if self.project.monitoring is not None:
                self.project.monitoring.stop()

     
    def filterPointCloud(self, maxconf: int = 3) -> None:
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('filterPointCloud',))
            thread.start()
        for chunk in self.project.doc.chunks:
            chunk.point_cloud.setConfidenceFilter(0, maxconf) # configuring point cloud filter so that only point with low-confidence currently active
            all_points_classes = list(range(128))
            chunk.point_cloud.removePoints(all_points_classes)  # removes all active points of the point cloud, i.e. removing all low-confidence points
            chunk.point_cloud.resetFilters()  # resetting filter, so that all other points (i.e. high-confidence points) are now active
        if self.project.monitoring is not None:
            self.project.monitoring.stop()

