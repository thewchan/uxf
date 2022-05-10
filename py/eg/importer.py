#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import importlib
import importlib.util
import os
import sys


def import_module(name, location):
    path = os.path.abspath('.')
    os.chdir(os.path.dirname(__file__))
    spec = importlib.util.spec_from_file_location(name, location)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    os.chdir(path)
    return module
