# SPDX-FileCopyrightText: 2022 - 2025 Peter Urban, Ghent University
#
# SPDX-License-Identifier: MPL-2.0

"""
Helper to expose C++ submodules in Python wrapper packages.

This enables both import styles:
  - from themachinethatgoesping.module import submodule
  - import themachinethatgoesping.module.submodule
"""

import sys
import types


def expose_submodules(cpp_module, package_name):
    """
    Dynamically expose all submodules from a C++ binding module.

    Args:
        cpp_module: The C++ binding module (e.g., algorithms_nanopy)
        package_name: Full package name (e.g., 'themachinethatgoesping.algorithms')

    Returns:
        dict: Dictionary of direct submodule names to module objects to add to globals()
    """

    def _register(full_name, module):
        existing = sys.modules.get(full_name)
        if existing is not module:
            sys.modules[full_name] = module
        # Keep module metadata consistent for importlib and friends.
        if getattr(module, "__package__", None) != full_name:
            try:
                module.__package__ = full_name
            except AttributeError:
                # Built-in/extension modules may forbid attribute assignment.
                pass

    visited = {id(cpp_module)}
    direct_submodules = {}

    # Keep the existing Python package module if it already exists in sys.modules.
    package_module = sys.modules.get(package_name)
    if package_module is None:
        sys.modules[package_name] = cpp_module
    else:
        visited.add(id(package_module))

    def _walk(module, module_name, is_root):
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue

            attr = getattr(module, attr_name)
            if not isinstance(attr, types.ModuleType):
                continue

            full_name = f"{module_name}.{attr_name}"
            existing = sys.modules.get(full_name)
            if existing is not attr:
                sys.modules[full_name] = attr

            if is_root:
                direct_submodules[attr_name] = attr

            attr_id = id(attr)
            if attr_id in visited:
                continue

            visited.add(attr_id)
            _walk(attr, full_name, False)

    _walk(cpp_module, package_name, True)
    return direct_submodules
