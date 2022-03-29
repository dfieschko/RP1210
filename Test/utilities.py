import configparser
import warnings

class RP1210ConfigTestUtility():

    def __init__(self, config : configparser.ConfigParser):
        self._config = config

    def verifydata(self, func, section : str, field : str):
        """
        Used to assist in testing by testing standard config information
        Usage:
            assert TestUtility.verifydata([function to test], [section], "[field]")
        """
        if not self._config.has_option(section, field):
            warnings.warn(UserWarning("could not find data at [" + section + "][" + field + "]"))
            return True
    
        retType = func.__annotations__["return"]
        if retType is str:
            return func() == self._config.get(section, field)
        
        if retType is bool:
            return func() == self._config.getboolean(section, field)

        if retType is int:
            return func() == self._config.getint(section, field)

        if retType is float:
            return func() == self._config.getfloat(section, field)
            
        else:
            list_vals = self._config.get(section, field).split(',')
            if list_vals != ['']:
                list_vals = list(map(int, list_vals))
            else:
                list_vals = []
            return func() == list_vals
