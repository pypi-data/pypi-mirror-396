
class Magnitude:
    """Base class for physical magnitudes
    
    A physical magnitude comprises a numerical value with units.

    The magnitude is converted to SI units as it is defined. The
    original value and units are still preserved.
    """

    def __init__(self, val, unit=None):
        self.set(val, unit)

    def set(self, val, unit):
        """Set a new value and unit"""
        self._oval = val
        self._ounit = unit
        self._convert(val, unit)

    @property
    def value(self):
        """Return the original value and units"""
        return self._oval, self._ounit
    
    
    @property
    def x(self):
        """Return the converted value"""
        return self._x

    @property
    def unit(self):
        """Return the converted unit"""
        raise(NotImplementedError, "Units not defined")

    def list_units():
        raise(NotImplementedError, "list of units not implemented")
    
    def _convert(self, val, units):
        raise(NotImplementedError, "Conversion not implemented")
    
    def _check_unit(self, unit, unit_dict):
        if unit in unit_dict.keys():
            return unit
        else:
            for k, v in unit_dict.items():
                if unit in v:
                    return k
            return None
        

