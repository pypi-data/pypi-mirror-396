# SPDX-FileCopyrightText: 2022 - 2025 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

# Import all symbols from the C++ module
from themachinethatgoesping.navigation_nanopy import *  # flake8: noqa

# Dynamically expose all C++ submodules
from themachinethatgoesping.tools._submodule_helper import expose_submodules
from themachinethatgoesping import navigation_nanopy

globals().update(expose_submodules(navigation_nanopy, 'themachinethatgoesping.navigation'))
del navigation_nanopy, expose_submodules

__version__ = "@PROJECT_VERSION@"
