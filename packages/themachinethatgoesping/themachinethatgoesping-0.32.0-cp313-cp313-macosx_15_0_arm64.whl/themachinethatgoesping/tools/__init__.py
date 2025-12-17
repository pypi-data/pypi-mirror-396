# SPDX-FileCopyrightText: 2022 - 2023 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

from . import timeconv as timeconv_ext  # flake8: noqa

# Import all symbols from the C++ module
from themachinethatgoesping.tools_nanopy import *  # flake8: noqa

# Dynamically expose all C++ submodules
from ._submodule_helper import expose_submodules
from themachinethatgoesping import tools_nanopy

globals().update(expose_submodules(tools_nanopy, 'themachinethatgoesping.tools'))
del tools_nanopy, expose_submodules

# overwrite timeconv module using the loaded python extension
timeconv = timeconv_ext

__version__ = "@PROJECT_VERSION@"
