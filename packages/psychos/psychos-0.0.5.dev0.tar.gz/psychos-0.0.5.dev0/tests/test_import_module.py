import importlib
import pkgutil
import pytest


# Test for all submodules inside psychos
@pytest.mark.parametrize(
    "module_name",
    [
        name
        for _, name, _ in pkgutil.walk_packages(
            importlib.import_module("psychos").__path__, "psychos."
        )
    ],
)
def test_import_module(module_name):
    """
    Test to ensure all modules and submodules in the psychos package can be imported
    without raising an ImportError.

    Parameters
    ----------
    module_name : str
        The name of the module or submodule to import.
    """
    try:
        importlib.import_module(module_name)
    except ImportError as e:
        pytest.fail(f"Failed to import {module_name}: {e}")


# Test for the top-level psychos module
def test_import_top_level_module():
    """
    Test to ensure the top-level psychos module can be imported
    without raising an ImportError.
    """
    try:
        importlib.import_module("psychos")
    except ImportError as e:
        pytest.fail(f"Failed to import top-level module 'psychos': {e}")
