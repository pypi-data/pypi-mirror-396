import os
from assorthead import includes, licenses

__author__ = "Aaron Lun"
__copyright__ = "Aaron Lun"
__license__ = "MIT"


def test_includes():
    out = includes()
    assert isinstance(out, str)
    assert os.path.isdir(os.path.join(out, "annoy"))
    assert os.path.isdir(os.path.join(out, "byteme"))


def test_licenses():
    out = licenses()
    assert isinstance(out, str)
    assert os.path.isdir(os.path.join(out, "annoy"))
    assert os.path.isdir(os.path.join(out, "byteme"))
