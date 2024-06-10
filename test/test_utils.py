import unittest
from unittest.mock import patch, Mock
from src.utils import check_version

class TestCheckVersion(unittest.TestCase):
    @patch('src.utils.Metashape')
    def test_check_version_compatible(self, mock_metashape):
        mock_app = Mock()
        mock_app.version = '2.1.0'
        mock_metashape.app = mock_app

        # should not except if compatible version
        check_version()

    @patch('src.utils.Metashape')
    def test_check_version_incompatible(self, mock_metashape):
        mock_app = Mock()
        mock_app.version = '2.2.0'
        mock_metashape.app = mock_app

        # It should raise an exception if the version is not compatible
        with self.assertRaises(Exception):
            check_version()

    @patch('src.utils.Metashape')
    def test_check_version_different_format(self, mock_metashape):
        mock_app = Mock()
        mock_app.version = '2'
        mock_metashape.app = mock_app
        with self.assertRaises(Exception):
            check_version()

    @patch('src.utils.Metashape')
    def test_check_version_invalid_string(self, mock_metashape):
        mock_app = Mock()
        mock_app.version = '2.abc'
        mock_metashape.app = mock_app
        with self.assertRaises(Exception):
            check_version()

    @patch('src.utils.Metashape')
    def test_check_version_none(self, mock_metashape):
        mock_app = Mock()
        mock_app.version = None
        mock_metashape.app = mock_app
        with self.assertRaises(Exception):
            check_version()

if __name__ == '__main__':
    unittest.main()
