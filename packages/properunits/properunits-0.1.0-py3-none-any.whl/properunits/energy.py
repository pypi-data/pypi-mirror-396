from .base import Magnitude

_en_names = {
    'J' : ['Joules', 'joule', 'joules'],
    'eV' : ['ev'],
    'cal' : ['Cal', 'calories'],
    'kWh' : ['kiloWatt hour'],
    'Btu' : ['BTU']
}

_en_conv = {
    'eV' : lambda x: 1.6021767e-19*x,
    'cal' : lambda x: 4.184*x,
    'kWh' : lambda x: 3.6e6*x,
    'Btu' : lambda x: 1.0551e3*x
}

class Energy(Magnitude):
    """Energy magnitude with automatic conversion to SI units (Joules).

    The Energy class represents physical energy quantities and automatically
    converts input values to the SI unit (Joules) regardless of the input unit.
    The class supports various common energy units including eV, calories, kWh, and BTU.

    Attributes:
        _unit (str): The SI unit for energy (Joules, 'J')

    Supported Units:
        - 'J': Joules (SI unit) - also accepts 'Joules', 'joule', 'joules'
        - 'eV': electron volts - also accepts 'ev'
        - 'cal': calories - also accepts 'Cal', 'calories'
        - 'kWh': kilowatt-hours - also accepts 'kiloWatt hour'
        - 'Btu': British thermal units - also accepts 'BTU'

    Examples:
        >>> en = Energy(5, 'cal')
        >>> en.x  # Value in Joules (SI)
        20.92
        >>> en.value  # Original value and unit
        (5, 'cal')
        >>> en.unit
        'J'

        >>> en2 = Energy(1, 'eV')
        >>> en2.x  # Value in Joules
        1.6021767e-19

        >>> Energy.list_units()
        ['J', 'eV', 'cal', 'kWh', 'Btu']

    Notes:
        - Input values are immediately converted to Joules upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
    """

    _unit = 'J'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _en_names)
        if key == Energy._unit:
            self._x = val
        else:
            self._x = _en_conv[key](val)

    @property
    def unit(self):
        return Energy._unit

    def list_units():
        return list(_en_names.keys())
