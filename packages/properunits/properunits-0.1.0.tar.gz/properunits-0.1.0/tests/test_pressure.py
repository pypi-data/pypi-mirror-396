from properunits import Pressure
import pytest


def test_pressure():
    p = Pressure(100, 'bar')
    assert p.x == pytest.approx(1e7)

def test_pressure_units():
    Pressure.list_units()
    
    