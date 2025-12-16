from properunits import Mass
import pytest


def test_mass():
    m = Mass(100, 'lb')
    assert m.x == pytest.approx(45.359237)


def test_mass_units():
    Mass.list_units()
    
    