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

        self.set_cpu(self.default_settings["cpu_enable"])
        self.set_gpu_mask(self.default_settings["gpu_mask"])

    # TODO DEBUG 
    #def stampare(self):
    #    print(self.default_settings)

    """
    set CPU when performing GPU accelerated processing
    """
    def set_cpu(self, cpu_status: bool = False) -> None:
        Metashape.app.cpu_enable = cpu_status
        print("--CPU STATUS:", Metashape.app.cpu_enable)

    """
    enable GPUs from input gpu_mask or enable all available
    """
    def set_gpu_mask(self, gpu_mask: str) -> None:
        if gpu_mask:
            # Convert binary string to int
            print(gpu_mask)
            gpu_mask = int(gpu_mask, 2)
        else:
            # enable all GPUs
            gpuBinary = ""
            gpus = Metashape.app.enumGPUDevices()
            print(gpus)
            for gpu in gpus:
                gpuBinary += "1"
            if gpuBinary == "": gpuBinary = "0"

            # Convert binary string to int
            gpu_mask = int(gpuBinary,2)

        Metashape.app.gpu_mask = gpu_mask
        print(Metashape.app.gpu_mask)

    


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

