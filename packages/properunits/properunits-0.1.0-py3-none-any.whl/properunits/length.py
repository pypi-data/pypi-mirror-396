from .base import Magnitude

_length_names = {
    'm' : ['meter'],
    'nm' : ['nanometers'],
    'A' : ['Angstroms'],
    'in' : ['inch', 'inches'],
    'mi' : ['mile', 'miles'],
    'yd' : ['yard', 'yards'],
    'ft' : ['foot', 'feet']
}

_length_conv = {
    'nm' : lambda x: 1e-9*x,
    'A' : lambda x: 1e-10*x,
    'in' : lambda x: 2.54e-2*x,
    'mi' : lambda x: 1609.34*x,
    'yd' : lambda x: 0.9144*x,
    'ft' : lambda x: 0.3048*x
}

_area_names = {
    'm2' : ['m^2'],
    'nm2' : ['nm^2'],
    'A2' : ['A^2'],
    'ha' : ['hectarea'],
    'ac' : ['acre']
}

_area_conv = {
    'nm2' : lambda x: 1e-18*x,
    'A2' : lambda x: 1e-20*x,
    'ha' : lambda x: 1e4*x,
    'ac' : lambda x: 4046.856*x
}

_volume_names = {
    'l' : ['liter', 'liters'],
    'cm3' : ['cm^3'],
    'm3' : ['m^3'],
    'gal' : ['gallons', 'gallon']
}

_volume_conv = {
    'l' : lambda x: 1e-6*x,
    'cm3' : lambda x: 1e-6*x,
    'gal' : lambda x: 3.785411784e-6*x
}


class Length(Magnitude):
    """Length magnitude with automatic conversion to SI units (meters).

    The Length class represents physical length quantities and automatically
    converts input values to the SI unit (meters) regardless of the input unit.
    The class supports various common length units including metric and imperial systems.

    Attributes:
        _unit (str): The SI unit for length (meters, 'm')

    Supported Units:
        - 'm': meters (SI unit) - also accepts 'meter'
        - 'nm': nanometers - also accepts 'nanometers'
        - 'A': Angstroms - also accepts 'Angstroms'
        - 'in': inches - also accepts 'inch', 'inches'
        - 'mi': miles - also accepts 'mile', 'miles'
        - 'yd': yards - also accepts 'yard', 'yards'
        - 'ft': feet - also accepts 'foot', 'feet'

    Examples:
        >>> length = Length(12, 'in')
        >>> length.x  # Value in meters (SI)
        0.3048
        >>> length.value  # Original value and unit
        (12, 'in')
        >>> length.unit
        'm'

        >>> length2 = Length(5, 'ft')
        >>> length2.x  # Value in meters
        1.524

        >>> Length.list_units()
        ['m', 'nm', 'A', 'in', 'mi', 'yd', 'ft']

    Notes:
        - Input values are immediately converted to meters upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
    """

    _unit = 'm'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _length_names)
        if key == Length._unit:
            self._x = val
        else:
            self._x = _length_conv[key](val)

    @property
    def unit(self):
        return Length._unit

    def list_units():
        return list(_length_names.keys())


class Area(Magnitude):
    """Area magnitude with automatic conversion to SI units (square meters).

    The Area class represents physical area quantities and automatically
    converts input values to the SI unit (square meters) regardless of the input unit.
    The class supports various common area units including metric and imperial systems.

    Attributes:
        _unit (str): The SI unit for area (square meters, 'm2')

    Supported Units:
        - 'm2': square meters (SI unit) - also accepts 'm^2'
        - 'nm2': square nanometers - also accepts 'nm^2'
        - 'A2': square Angstroms - also accepts 'A^2'
        - 'ha': hectares - also accepts 'hectarea'
        - 'ac': acres - also accepts 'acre'

    Examples:
        >>> area = Area(1, 'ha')
        >>> area.x  # Value in square meters (SI)
        10000.0
        >>> area.value  # Original value and unit
        (1, 'ha')
        >>> area.unit
        'm2'

        >>> area2 = Area(5, 'ac')
        >>> area2.x  # Value in square meters
        20234.28

        >>> Area.list_units()
        ['m2', 'nm2', 'A2', 'ha', 'ac']

    Notes:
        - Input values are immediately converted to square meters upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
    """

    _unit = 'm2'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _area_names)
        if key == Area._unit:
            self._x = val
        else:
            self._x = _area_conv[key](val)

    @property
    def unit(self):
        return Area._unit

    def list_units():
        return list(_area_names.keys())


class Volume(Magnitude):
    """Volume magnitude with automatic conversion to SI units (cubic meters).

    The Volume class represents physical volume quantities and automatically
    converts input values to the SI unit (cubic meters) regardless of the input unit.
    The class supports various common volume units including liters, cubic centimeters, and gallons.

    Attributes:
        _unit (str): The SI unit for volume (cubic meters, 'm3')

    Supported Units:
        - 'm3': cubic meters (SI unit) - also accepts 'm^3'
        - 'l': liters - also accepts 'liter', 'liters'
        - 'cm3': cubic centimeters - also accepts 'cm^3'
        - 'gal': gallons - also accepts 'gallon', 'gallons'

    Examples:
        >>> vol = Volume(10, 'l')
        >>> vol.x  # Value in cubic meters (SI)
        1e-05
        >>> vol.value  # Original value and unit
        (10, 'l')
        >>> vol.units  # Note: uses 'units' property
        'm3'

        >>> vol2 = Volume(5, 'gal')
        >>> vol2.x  # Value in cubic meters
        1.892705892e-05

        >>> Volume.list_units()
        ['l', 'cm3', 'm3', 'gal']

    Notes:
        - Input values are immediately converted to cubic meters upon instantiation
        - Original values and units are preserved and accessible via the `value` property
        - The converted SI value is accessible via the `x` property (inherited from Magnitude)
        - Unit names are case-sensitive for the primary keys but aliases are provided
        - Note: This class uses `units` property instead of `unit` (different from other classes)
    """

    _unit = 'm3'

    def _convert(self, val, unit):
        key = self._check_unit(unit, _volume_names)
        if key == Volume._unit:
            self._x = val
        else:
            self._x = _volume_conv[key](val)

    @property
    def units(self):
        return Volume._unit

    def list_units():
        return list(_volume_names.keys())
