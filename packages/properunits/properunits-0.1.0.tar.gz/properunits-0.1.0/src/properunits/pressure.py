from .base import Magnitude

_p_names = {
    'Pa' : ['Pa', 'Pascal', 'Pascals'],
    'Torr' : ['Torr', 'torr', 'Torrs'],
    'mTorr' : ['mTorr', 'mtorr'],
    'atm' : ['atm', 'Atm', 'Atmos'],
    'psi' : ['PSI', 'Psi'],
    'ksi' : ['KSI'],
    'bar' : ['bar', 'Bar', 'bars']
}

_p_conv = {
    'Torr' : lambda x: 133.322*x,
    'mTorr' : lambda x: 0.133322*x,
    'atm' : lambda x: 101325*x,
    'psi' : lambda x: 6.894757e3*x,
    'ksi' : lambda x: 6.894757e6*x,
    'bar' : lambda x: 1e5*x
}

class Pressure(Magnitude):
    """Pressure magnitude with automatic conversion to SI units (Pascals).

    The Pressure class represents physical pressure quantities and automatically
    converts input values to the SI unit (Pascals) regardless of the input unit.
    The class supports various common pressure units including Torr, atmospheres,
    psi, and bar.

    Attributes:
        _unit (str): The SI unit for pressure (Pascals, 'Pa')

    Supported Units:
        - 'Pa': Pascals (SI unit) - also accepts 'Pa', 'Pascal', 'Pascals'
        - 'Torr': Torr - also accepts 'Torr', 'torr', 'Torrs'
        - 'mTorr': milliTorr - also accepts 'mTorr', 'mtorr'
        - 'atm': atmospheres - also accepts 'atm', 'Atm', 'Atmos'
        - 'psi': pounds per square inch - also accepts 'PSI', 'Psi'
        - 'ksi': kilo-pounds per square inch - also accepts 'KSI'
        - 'bar': bar - also accepts 'bar', 'Bar', 'bars'

    Examples:
        >>> p = Pressure(1, 'atm')
        >>> p.x  # Value in Pascals (SI)
        101325.0
        >>> p.value  # Original value and unit
        (1, 'atm')
        >>> p.unit
        'Pa'

        >>> p2 = Pressure(100, 'psi')
        >>> p2.x  # Value in Pascals
        689475.7

        >>> Pressure.list_units()
        ['Pa', 'Torr', 'mTorr', 'atm', 'psi', 'ksi', 'bar']

    Notes:
        - Input values are immediately converted to Pascals upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
        - Commonly used in chemistry (Torr, atm) and engineering (psi, bar)
    """

    _unit = 'Pa'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _p_names)
        if key == Pressure._unit:
            self._x = val
        else:
            self._x = _p_conv[key](val)

    @property
    def unit(self):
        return Pressure._unit
    
    def list_units():
        return list(_p_names.keys())


