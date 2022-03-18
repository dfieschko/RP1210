import sys
import configparser, RP1210
from inspect import signature
import warnings



class TestUtility():

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
            
        elif type(retType[0]) is int:
            return func() == list(map(int, self._config.get(section, field).split(',')))