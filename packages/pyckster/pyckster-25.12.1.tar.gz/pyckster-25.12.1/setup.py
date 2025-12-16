from setuptools import setup, find_packages
from pathlib import Path
import re

# Extract version info without importing the package
def read_version_info(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)
    author_match = re.search(r"^__author__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)
    email_match = re.search(r"^__email__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)
    license_match = re.search(r"^__license__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)
    
    info = {}
    if version_match:
        info['version'] = version_match.group(1)
    if author_match:
        info['author'] = author_match.group(1)
    if email_match:
        info['email'] = email_match.group(1)
    if license_match:
        info['license'] = license_match.group(1)
    
    return info

# Get version info from __init__.py
init_file = Path(__file__).parent / "pyckster" / "__init__.py"
info = read_version_info(str(init_file))

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pyckster",
    description="A PyQt5-based GUI for picking seismic traveltimes",
    author=info.get('author', 'Sylvain Pasquet'),  # Fallback if not found
    author_email=info.get('email', 'sylvain.pasquet@sorbonne-universite.fr'),
    version=info.get('version', '0.0.0'),
    url='https://gitlab.in2p3.fr/metis-geophysics/pyckster',
    license=info.get('license', 'GPLv3'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        "PyQt5>=5.15.4",
        "pyqtgraph",
        "numpy",
        "scipy",
        "matplotlib",
        "obspy",
    ],
    # Remove py_modules since you're using packages
    entry_points={
        'console_scripts': [
            'pyckster=pyckster.core:main',
            'pyckster-inversion=pyckster.inversion_app:main',
        ],
    },
    include_package_data=True,
    zip_safe=False
)