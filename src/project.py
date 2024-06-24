# project.py
import Metashape
from src.singleton_meta import SingletonMeta
from src.system_monitor import SystemMonitor
    
class Project(metaclass=SingletonMeta):
    def __init__(self, project_path: str = None, enable_monitoring: bool = False):
        self.project_path = project_path
        self.doc = None
        self.chunk = None
        self.monitoring = None
        
        if enable_monitoring:
            self.monitoring = SystemMonitor(project_path + "/monitor.csv")

    @classmethod
    def get_project(cls):
        return cls()

    def load_project(self):
        self.doc = Metashape.Document()
        self.doc.open(path=self.project_path, read_only=False)
        self.chunk = self.doc.chunk
        print("--Load Project", self.doc.path)

    def new_project(self):
        self.doc = Metashape.Document()
        self.save_project(path=self.project_path, version="New project")
        self.chunk = self.doc.addChunk()
        print("--New Project", self.doc.path)

    # project version to save
    def save_project(self, version: str, path: str = None):
        if path == None:
            self.doc.save(version=version)
        else:
            # init project case
            self.doc.save(path=path, version=version)

    def quit_project(self):
        Metashape.app.quit()
