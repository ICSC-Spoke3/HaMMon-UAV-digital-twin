# project.py
import Metashape

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            # TODO: se non va
            # cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class Project(metaclass=SingletonMeta):
    def __init__(self, project_path: str = None):
        self.project_path = project_path
        self.doc = None
        self.chunk = None

    @classmethod
    def get_project(cls):
        return cls()

    def load_project(self):
        self.doc = Metashape.app.Document
        self.doc.open(path=self.project_path, read_only=False)
        self.chunk = self.doc.chunk
        print("--Load Project", self.doc.path)
        # chunk.matchPhotos
        # chunk.alignCameras
        # buildDepthMaps
        # buildModel
        # buildUV
        # buildTexture
        # save()

    def new_project(self):
        self.doc = Metashape.Document()
        self.save_project(version="New project")
        self.chunk = self.doc.addChunk()
        print("--New Project", self.doc.path)

    # project version to save
    def save_project(self, version: str):
        self.doc.save(path=self.project_path, version=version)

    def quit_project(self):
        Metashape.app.quit()






