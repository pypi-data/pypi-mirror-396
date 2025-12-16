from .base import Magnitude

_T_names = {
    'C' : ['C', 'Celsius', 'Centigrades'],
    'K' : ['K', 'Kelvin'],
    'F' : ['F', 'Farenheit']
}

_T_conv = {
    'C' : lambda x: x + 273.15,
    'F' : lambda x: (x-32)/1.8
}

class Temperature(Magnitude):
    """Temperature magnitude with automatic conversion to SI units (Kelvin).

    The Temperature class represents physical temperature quantities and automatically
    converts input values to the SI unit (Kelvin) regardless of the input unit.
    The class supports common temperature scales including Celsius, Kelvin, and Fahrenheit.

    Attributes:
        _unit (str): The SI unit for temperature (Kelvin, 'K')

    Supported Units:
        - 'K': Kelvin (SI unit) - also accepts 'K', 'Kelvin'
        - 'C': Celsius - also accepts 'C', 'Celsius', 'Centigrades'
        - 'F': Fahrenheit - also accepts 'F', 'Farenheit'

    Examples:
        >>> temp = Temperature(25, 'C')
        >>> temp.x  # Value in Kelvin (SI)
        298.15
        >>> temp.value  # Original value and unit
        (25, 'C')
        >>> temp.units  # Note: uses 'units' property
        'K'

        >>> temp2 = Temperature(32, 'F')
        >>> temp2.x  # Value in Kelvin
        273.15

        >>> Temperature.list_units()
        ['C', 'K', 'F']

    Notes:
        - Input values are immediately converted to Kelvin upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
        - Note: This class uses `units` property instead of `unit` (different from other classes)
        - Celsius to Kelvin: K = C + 273.15
        - Fahrenheit to Kelvin: K = (F - 32) / 1.8
    """

    _unit = 'K'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _T_names)
        if key == Temperature._unit:
            self._x = val
        else:
            self._x = _T_conv[key](val)

    @property
    def unit(self):
        return Temperature._unit

    def list_units():
        return list(_T_names.keys())
