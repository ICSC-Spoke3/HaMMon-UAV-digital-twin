# settings.py
import Metashape
from src.version_checker import check_version


"""
  Agisoft settings preference
"""

class Settings:
    def __init__(self, input_values: dict = None):
        # set default settings
        self.default_settings = {
            'cpu_enable': True,
            'gpu_mask': 'Default',
            'log': 'default',
            'Default': 'Default'
        }

        # set input settings
        if input_values is not None:
            for key, value in input_values.items():
                if key in self.default_settings:
                    self.default_settings[key] = value

    def stampare(self):
        print(self.default_settings)


"""
set CPU when performing GPU accelerated processing
"""
def cpu_enable(cpu_status: bool = False):
    Metashape.app.cpu_enable = cpu_status
    print("--CPU STATUS", Metashape.app.cpu_enable)

"""
set GPUs mask
"""
def gpu_mask():
    pass

def run(parameters):
    check_version()
    print("Step 1", parameters)


"""
set log file
"""

"""
check version
"""

