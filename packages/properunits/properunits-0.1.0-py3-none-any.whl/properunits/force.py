from .base import Magnitude

_f_names = {
    'N' : ['Newton'],
    'dyn' : ['Dyne, dyne'],
    'lbf' : ['pound-force'],
    'pdl' : ['poundal']
}

_f_conv = {
    'dyn' : lambda x: 1e-5*x,
    'lbf' : lambda x: 4.448222*x,
    'pdl' : lambda x: 0.1382550*x
}

class Force(Magnitude):
    """Force magnitude with automatic conversion to SI units (Newtons).

    The Force class represents physical force quantities and automatically
    converts input values to the SI unit (Newtons) regardless of the input unit.
    The class supports various common force units including dynes, pound-force, and poundals.

    Attributes:
        _unit (str): The SI unit for force (Newtons, 'N')

    Supported Units:
        - 'N': Newtons (SI unit) - also accepts 'Newton'
        - 'dyn': dynes - also accepts 'Dyne, dyne'
        - 'lbf': pound-force - also accepts 'pound-force'
        - 'pdl': poundals - also accepts 'poundal'

    Examples:
        >>> f = Force(10, 'lbf')
        >>> f.x  # Value in Newtons (SI)
        44.48222
        >>> f.value  # Original value and unit
        (10, 'lbf')
        >>> f.unit
        'N'

        >>> f2 = Force(1000, 'dyn')
        >>> f2.x  # Value in Newtons
        0.01

        >>> Force.list_units()
        ['N', 'dyn', 'lbf', 'pdl']

    Notes:
        - Input values are immediately converted to Newtons upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
    """

    _unit = 'N'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _f_names)
        if key == Force._unit:
            self._x = val
        else:
            self._x = _f_conv[key](val)

    @property
    def unit(self):
        return Force._unit

    def list_units():
        return list(_f_names.keys())
