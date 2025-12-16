from .base import Magnitude

_mass_names = {
    'kg' : ['kilo'],
    'g' : ['gram'],
    'lb' : ['pound', 'lbs'],
    'oz' : ['ounce', 'ounces'],
    't' : ['tonne'],
    'Da' : ['u', 'amu']
}

_mass_conv = {
    'g' : lambda x: 1e-3*x,
    'lb' : lambda x: 0.45359237*x,
    'oz' : lambda x: 28.349523125e-3*x,
    't' : lambda x: 1e3*x,
    'Da' : lambda x: 1.66053906892e-27*x
}

class Mass(Magnitude):
    """Mass magnitude with automatic conversion to SI units (kilograms).

    The Mass class represents physical mass quantities and automatically
    converts input values to the SI unit (kilograms) regardless of the input unit.
    The class supports various common mass units including metric and imperial systems,
    as well as atomic mass units.

    Attributes:
        _unit (str): The SI unit for mass (kilograms, 'kg')

    Supported Units:
        - 'kg': kilograms (SI unit) - also accepts 'kilo'
        - 'g': grams - also accepts 'gram'
        - 'lb': pounds - also accepts 'pound', 'lbs'
        - 'oz': ounces - also accepts 'ounce', 'ounces'
        - 't': tonnes - also accepts 'tonne'
        - 'Da': Daltons (atomic mass units) - also accepts 'u', 'amu'

    Examples:
        >>> mass = Mass(5, 'lb')
        >>> mass.x  # Value in kilograms (SI)
        2.26796185
        >>> mass.value  # Original value and unit
        (5, 'lb')
        >>> mass.unit
        'kg'

        >>> mass2 = Mass(500, 'g')
        >>> mass2.x  # Value in kilograms
        0.5

        >>> Mass.list_units()
        ['kg', 'g', 'lb', 'oz', 't', 'Da']

    Notes:
        - Input values are immediately converted to kilograms upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
        - Daltons (Da) are useful for atomic and molecular masses
    """

    _unit = 'kg'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _mass_names)
        if key == Mass._unit:
            self._x = val
        else:
            self._x = _mass_conv[key](val)

    @property
    def unit(self):
        return Mass._unit

    def list_units():
        return list(_mass_names.keys())
