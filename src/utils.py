#utils.py
"""
This module provides utility functions for checking the application version.

Functions:
    check_version: Checks if the current version of the application is compatible with the required version.
"""
import Metashape

def check_version():
    """
    Checks if the current version of the application is compatible with the required version.

    The compatible version is 2.1. If the current version of the application is not compatible,
    this function raises an exception.

    Raises:
        Exception: If the current version of the application is not compatible with the required version.
    """
    compatible_major_version = "2.1"
    found_major_version = ".".join(Metashape.app.version.split('.')[:2])
    if found_major_version != compatible_major_version:
        raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))
