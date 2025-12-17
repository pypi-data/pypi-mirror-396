import importlib


def test_package_importable():
    mod = importlib.import_module("om")
    assert hasattr(mod, "cum")
    assert hasattr(mod, "teasing")
    assert hasattr(mod, "penetration")
    assert hasattr(mod, "cuddling")
    assert hasattr(mod, "fwb")
