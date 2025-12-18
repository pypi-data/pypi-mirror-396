"""Smoke test to prevent tox from failing"""
def test_package_imports():
    import ginsapy  # just verify the wheel installs & imports

def test_version_metadata_is_present():
    import importlib.metadata as im
    assert im.version("ginsapy")
