import configparser

class RP1210ConfigTestUtility():

    def __init__(self, config : configparser.ConfigParser):
        self._config = config

    def verifydata(self, func, section : str, field : str, fallback=None):
        """
        Used to assist in testing by testing standard config information
        Usage:
            assert TestUtility.verifydata([function to test], [section], "[field]")
        """
        # if not self._config.has_option(section, field):
        #     assert func() in ("", None, [], False, 0, 1, -1, 1024, "(Vendor Name Missing)")
        #     return
        func_return = func()
    
        retType = func.__annotations__["return"]
        if retType is str:
            if fallback is None:
                fallback = ""
            val = self._config.get(section, field, fallback=fallback)
            assert func_return == val
        
        elif retType is bool:
            try:
                val = self._config.getboolean(section, field)
            except:
                val = fallback
            assert func_return == val

        elif retType is int:
            try:
                val = self._config.getint(section, field)
            except: # not RP1210 package's fault if ConfigParser failed to retrieve value
                val = fallback
            assert func_return == val

        elif retType is float:
            try:
                val = self._config.getfloat(section, field)
            except: # not RP1210 package's fault if ConfigParser failed to retrieve value
                val = fallback
            assert func_return == val
            
        elif retType is list[int]:
            list_vals = self._config.get(section, field).split(',')
            if list_vals != ['']:
                list_vals = list(map(int, list_vals))
            else:
                list_vals = []
            assert func_return == list_vals

        elif retType is list[str]:
            list_vals = self._config.get(section, field).split(',')
            if list_vals != ['']:
                list_vals = list(map(str, list_vals))
            else:
                list_vals = []
            assert func_return == list_vals

    def verifydevicedata(self, func, device_id, field):
        section = "DeviceInformation" + str(device_id)
        return self.verifydata(func, section, field)

    def verifyprotocoldata(self, func, protocol_id, field):
        section = "ProtocolInformation" + str(protocol_id)
        return self.verifydata(func, section, field)
