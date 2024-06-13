import unittest
from unittest.mock import patch, Mock
import Metashape
from src.settings import Settings

class TestSettings(unittest.TestCase):
    def setUp(self):
        self.obj = Settings()

    def tearDown(self):
        del self.obj

    # check_version
    def test_check_version_compatible(self):
        with patch('Metashape.app', new=Mock(version="2.1.0")):
            try:
                self.obj.check_version()  # Non dovrebbe sollevare eccezioni
            except Exception as e:
                self.fail(f"check_version() ha sollevato {type(e)} con una versione compatibile")
    
    def test_check_version_incompatible(self):
        with patch('Metashape.app', new=Mock(version="2.2.0")):
            with self.assertRaises(Exception) as context:
                self.obj.check_version()
            self.assertEqual(str(context.exception), "Incompatible Metashape version: 2.2 != 2.1")

    # set_cpu
    def test_set_cpu(self):
        self.obj.set_cpu(True)
        self.assertEqual(Metashape.app.cpu_enable, True, "cpu_status should be True")

        self.obj.set_cpu(False)
        self.assertEqual(Metashape.app.cpu_enable, False, "cpu_status should be False")
    
    def test_set_cpu_invalid_value(self):
        with self.assertRaises(TypeError):
            self.obj.set_cpu("non_bool")

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
