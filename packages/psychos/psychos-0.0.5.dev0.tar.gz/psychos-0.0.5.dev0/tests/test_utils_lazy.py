import pytest
import sys
import time
from psychos.utils.lazy import attach


# Simulate a package and submodules for the test
@pytest.fixture
def lazy_attach_setup():
    """Fixture to setup lazy loading for psychos.core.wait."""
    package_name = "psychos"
    submodules = ["core"]
    submod_attrs = {"core": ["wait"]}

    __getattr__, __dir__, __all__ = attach(
        package_name, submodules=submodules, submod_attrs=submod_attrs
    )

    yield __getattr__, __dir__, __all__

    # Cleanup the modules from sys.modules
    for mod in submodules:
        sys.modules.pop(f"{package_name}.{mod}", None)


def test_lazy_import_core_wait(lazy_attach_setup):
    """Test lazy import of psychos.core.wait."""
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Access the wait attribute (should trigger lazy import)
    wait_func = __getattr__("wait")

    # Check that the function works
    assert callable(wait_func)


def test_lazy_import_time(lazy_attach_setup):
    """Test lazy import of the standard time.time function."""
    # Access the time.time function directly (no need for the lazy attach system)
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Ensure that time is imported directly from the standard library
    assert "time" in sys.modules

    # Access the time function and ensure it is callable
    time_func = time.time
    assert callable(time_func)
    assert time_func() <= time.time() + 1  # Compare to current time to ensure it works


def test_attr_error_handling(lazy_attach_setup):
    """Test handling of attribute errors."""
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Try to access a non-existing attribute
    with pytest.raises(AttributeError):
        __getattr__("non_existing_attr")


def test_dir_method(lazy_attach_setup):
    """Test the __dir__ method for listing attributes."""
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Check that all the attributes are listed properly
    assert "wait" in __dir__()


def test_lazy_import_core_submodule(lazy_attach_setup):
    """Test lazy import of a submodule like psychos.core."""
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Ensure that psychos.core is not imported initially
    assert "psychos.core" not in sys.modules

    # Access the 'core' submodule (should trigger lazy import)
    core_module = __getattr__("core")

    # Now the submodule should be imported
    assert "psychos.core" in sys.modules

    # Ensure that it's the correct module
    assert core_module.__name__ == "psychos.core"


def test_default_submod_attrs():
    """Test default value for submod_attrs when None is passed."""
    # Call attach without specifying submod_attrs (defaults to None)
    package_name = "psychos"
    __getattr__, __dir__, __all__ = attach(package_name, submodules=["core"])

    # Access a submodule to verify functionality
    assert __getattr__("core") is not None

    # Verify that the default value of submod_attrs is set to an empty dict
    assert isinstance(__all__, list)
    assert "core" in __all__


def test_dir_function(lazy_attach_setup):
    """Test that __dir__ returns the correct __all__ list."""
    __getattr__, __dir__, __all__ = lazy_attach_setup

    # Verify that __dir__ returns the correct __all__ content
    assert __dir__() == __all__
    assert "core" in __dir__()
    assert "wait" in __dir__()


def test_conflict_name_attribute():
    """Test that the attribute is assigned to the package's __dict__."""

    # Define the package name and the attribute we want to attach
    package_name = "psychos"
    submod_attrs = {"__version__": ["__version__"]}

    # Attach the attribute
    __getattr__, __dir__, __all__ = attach(package_name, submod_attrs=submod_attrs)

    # Access the attribute
    version = __getattr__("__version__")

    # Assert that version is a string
    assert isinstance(version, str)
