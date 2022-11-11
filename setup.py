import os
import sys
from distutils.core import setup

import py2exe

sys.argv.append('py2exe')

setup(
    options = {'py2exe': {'bundle_files': 1, 'compressed': True}},
    package_dir = {'': 'data'},
    windows = [{'script': 'C:/Program Files/Microsoft VS Code/repos/Movie-Dubber'}],
    zipfile = None,
)