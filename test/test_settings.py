import unittest
import Metashape
from src.settings import Settings

class TestSettings(unittest.TestCase):
    def setUp(self):
        self.obj = Settings()

    def tearDown(self):
        del self.obj

    # set_gpu_mask
    def test_set_gpu_mask(self):
        self.obj.set_gpu_mask("10")
        self.assertEqual(Metashape.app.gpu_mask, 2)
        self.obj.set_gpu_mask("01")
        self.assertEqual(Metashape.app.gpu_mask, 1)
        self.obj.set_gpu_mask("11")
        self.assertEqual(Metashape.app.gpu_mask, 2**len(Metashape.app.enumGPUDevices()) - 1)

    def test_set_gpu_mask_none(self):
        self.obj.set_gpu_mask(None)
        self.assertEqual(Metashape.app.gpu_mask, 2**len(Metashape.app.enumGPUDevices()) - 1)

    def test_set_gpu_mask_empty_string(self):
        self.obj.set_gpu_mask("")
        self.assertEqual(Metashape.app.gpu_mask, 2**len(Metashape.app.enumGPUDevices()) - 1)

    def test_set_gpu_mask_exceeds(self):
        gpu_mask = "1" * (len(Metashape.app.enumGPUDevices()) + 1)  # un numero di GPU maggiore di quelle disponibili
        self.obj.set_gpu_mask(gpu_mask)
        self.assertEqual(Metashape.app.gpu_mask, 2**len(Metashape.app.enumGPUDevices()) - 1)

    
    

if __name__ == '__main__':
    unittest.main()
