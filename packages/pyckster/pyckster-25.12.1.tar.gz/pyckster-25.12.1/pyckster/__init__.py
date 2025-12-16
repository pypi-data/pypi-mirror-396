"""
Pyckster - A PyQt5-based GUI for picking seismic traveltimes and analyzing inversions
"""

# Set matplotlib backend to prevent popup windows before any imports
# This must be done before any matplotlib imports anywhere in the codebase
import os
os.environ['MPLBACKEND'] = 'Agg'  # Set environment variable first

try:
    import matplotlib
    if not matplotlib.get_backend() == 'Agg':
        matplotlib.use('Agg')  # Use non-interactive backend
except ImportError:
    pass  # matplotlib not available, that's fine

# Define version and metadata in one place
__version__ = "25.12.1"
__author__ = "Sylvain Pasquet"
__email__ = "sylvain.pasquet@sorbonne-universite.fr"
__license__ = "GPLv3"

# Import and expose main functionality
from .core import main, MainWindow

# Define what's available when doing 'from pyckster import *'
__all__ = [
    'main',
    'MainWindow',
    '__version__',
]