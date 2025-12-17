"""
Pyseter
Processing images before photo-identification
"""

__version__ = "0.2.2"

# Import main functions/classes for easy access
from pyseter.extract import verify_pytorch, get_best_device

# Define what gets imported with "from your_package import *"
__all__ = ["verify_pytorch", "get_best_device"]