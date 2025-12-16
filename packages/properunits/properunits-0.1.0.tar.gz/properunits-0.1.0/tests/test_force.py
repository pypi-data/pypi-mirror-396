from properunits import Force
import pytest


def test_force():
    f = Force(100, 'dyn')
    assert f.x == pytest.approx(1e-3)

def test_force_units():
    Force.list_units()
    
    