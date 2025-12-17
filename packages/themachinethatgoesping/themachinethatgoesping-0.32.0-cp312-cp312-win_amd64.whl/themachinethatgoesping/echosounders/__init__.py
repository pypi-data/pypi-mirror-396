# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

import importlib
from pkgutil import extend_path as __extend_path__

# Import all symbols from the C++ module
from themachinethatgoesping.echosounders_nanopy import *  # flake8: noqa

# Dynamically expose all C++ submodules
from themachinethatgoesping.tools._submodule_helper import expose_submodules
from themachinethatgoesping import echosounders_nanopy

globals().update(expose_submodules(echosounders_nanopy, 'themachinethatgoesping.echosounders'))
del echosounders_nanopy, expose_submodules

# python only modules
from .index_functions import get_index_paths, find_files  # flake8: noqa
from .evaluate.evaluate_ping_features import evaluate_ping_features_can_be_called  # flake8: noqa

__version__ = "@PROJECT_VERSION@"
