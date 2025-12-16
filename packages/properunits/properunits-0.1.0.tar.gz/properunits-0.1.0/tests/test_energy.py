from properunits import Energy
import pytest


def test_energy():
    en = Energy(100, 'BTU')
    assert en.x == pytest.approx(1.0551e5)

def test_energy_units():
    Energy.list_units()

def test_energy_unit_property():
    """Test that the unit property returns the SI unit 'J' for Energy."""
    en1 = Energy(100, 'BTU')
    assert en1.unit == 'J'

    en4 = Energy(10, 'J')
    assert en4.unit == 'J'

def test_energy_value_method():
    """Test that the value property returns the original value and unit."""
    en1 = Energy(100, 'BTU')
    val, unit = en1.value
    assert val == 100
    assert unit == 'BTU'

    en4 = Energy(3.6e6, 'J')
    val, unit = en4.value
    assert val == 3.6e6
    assert unit == 'J'

def test_energy_value_with_aliases():
    """Test that value property preserves the exact unit string used, including aliases."""
    en1 = Energy(100, 'joules')
    val, unit = en1.value
    assert val == 100
    assert unit == 'joules'

    en2 = Energy(5, 'calories')
    val, unit = en2.value
    assert val == 5
    assert unit == 'calories'

