from properunits import Temperature
import pytest


def test_temperature():
    temp = Temperature(100, 'C')
    assert temp.x == pytest.approx(373.15)

def test_temperature_units():
    Temperature.list_units()
    
    