import pytest

from govdocs.marc import is_serial


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("01789nas a2200457 i 4500", True),
        ("02416cam a2200493 a 4500", False),
        ("02312cai a2200505 a 4500", False),
        ("02312cab a2200505 a 4500", True),
    ],
)
def test_is_serial(arg, expectation):
    assert is_serial(arg) == expectation
