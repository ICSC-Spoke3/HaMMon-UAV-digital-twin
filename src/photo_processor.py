# photo_processor.py
import threading
from src.project import Project

"""
Esegue l'inserimento delle foto, il filtro qualità, il match delle foto e l'allineamento di queste, 
possibile anche l'ottimizzazione della posizione delle camere e per poi creare la nuvola sparsa di punti
"""

class PhotoProcessor:

    def __init__(self, photos_path: str = None) -> None:
        self.project = Project.get_project()
        self.photos_path = photos_path

    """
    Add a list of photos to the chunk.
    """
    def addPhotos(self, progress_printer: str) -> None:
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('addPhotos',))
            thread.start()
        self.project.chunk.addPhotos(filenames=self.photos_path,
                                     progress=progress_printer)
        # NOTE: load_reference(bool) in addPhotos [https://www.agisoft.com/forum/index.php?topic=13603.0]
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="addPhotos")
        print("-- DEBUG: "+ str(len(self.project.chunk.cameras)) + " images loaded")
    
    """
    Estimate the image quality. Cameras with a quality less than 0.5 are considered blurred and it’s recommended to disable them.
    """
    def filterImageQuality(self, progress_printer: str) -> None:
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('filterImageQuality',))
            thread.start()
        self.project.chunk.analyzeImages(cameras=self.project.chunk.cameras,
                                         filter_mask= True,
                                         progress=progress_printer)
        # FIXME: filter_mask, delete it if not necessary
        print()
        num_disable_photos = 0
        for camera in self.project.chunk.cameras:
            if float(camera.meta['Image/Quality']) < 0.5:
                camera.enabled = False
                num_disable_photos += 1

        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        print("-- DEBUG: "+ str(num_disable_photos) + " images filtered")
        self.project.save_project(version="filterImageQuality")


    """
    Perform image matching
    """
    def matchPhotos(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'downscale': 1,
            'keypoint_limit': 40000,
            'tiepoint_limit': 10000,
            'generic_preselection': True,
            'reference_preselection': False,
            'filter_stationary_points': True,
            'keep_keypoints': True,
            'guided_matching': False,
            'subdivide_task': True
        }
        # NOTE: filter_mask (bool) – Filter points by mask
        # NOTE: pairs (list[tuple[int, int]]) – User defined list of camera pairs to match.
        # update default params with the input
        default_params.update(kwargs)
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('matchPhotos',))
            thread.start()
        self.project.chunk.matchPhotos(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="matchPhotos")
    
    """
    Perform photo alignment
    """
    def alignCameras(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'adaptive_fitting': False,
            'reset_alignment': False,
            'subdivide_task': True
        }
        # update default params with the input
        default_params.update(kwargs)
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('alignCameras',))
            thread.start()
        self.project.chunk.alignCameras(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="alignCameras")

    """
    Perform optimization of tie points / camera parameters
    """
    def optimizeCameras(self, progress_printer: str, **kwargs) -> None:
        default_params = {
            'fit_f': True, 
            'fit_cx': True, 
            'fit_cy': True, 
            'fit_b1': False, 
            'fit_b2': False, 
            'fit_k1': True,
            'fit_k2': True, 
            'fit_k3': True, 
            'fit_k4': False, 
            'fit_p1': True, 
            'fit_p2': True, 
            'fit_corrections': False,
            'adaptive_fitting': False, 
            'tiepoint_covariance': False
        }
        # update default params with the input
        default_params.update(kwargs)
        if self.project.monitoring is not None:
            thread = threading.Thread(target=self.project.monitoring.start, args=('optimizeCameras',))
            thread.start()
        self.project.chunk.optimizeCameras(progress=progress_printer, **default_params)
        if self.project.monitoring is not None:
            self.project.monitoring.stop()
        self.project.save_project(version="optimizeCameras")

    