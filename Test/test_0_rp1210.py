from configparser import ConfigParser
from ctypes import CDLL
import os
from RP1210 import sanitize_msg_param
import RP1210
import pytest
from mock import patch
from ctypes import cdll
from ctypes import POINTER, c_char_p, c_int32, c_long, c_short, c_void_p, cdll, CDLL, create_string_buffer

API_NAMES = ["PEAKRP32", "DLAUSB32", "DGDPA5MA", "NULN2R32",
             "CMNSI632", "CIL7R32", "DrewLinQ", "DTKRP32"]
INVALID_API_NAMES = ["empty_api", "invalid_api",
                     "extra_empty_api", "invalid_pd_api"]

# These tests are meant to be run with cwd @ repository's highest-level directory
CWD = os.getcwd()
TEST_FILES_DIRECTORY = CWD + ".\\Test\\test-files"
INI_DIRECTORY = TEST_FILES_DIRECTORY + "\\ini-files"
DLL_DIRECTORY = TEST_FILES_DIRECTORY + "\\dlls"
RP121032_PATH = TEST_FILES_DIRECTORY + "\\RP121032.ini"

def delete_file(path : str):
    if os.path.exists(path):
        os.remove(path)

def create_file(path : str) -> ConfigParser:
    """creates an empty file."""
    parser = ConfigParser()
    with open(path, 'w') as file:
        parser.clear()
        parser.write(file)
    return parser

def test_RP1210Interface_InvalidAPIName():
    """
    Tests the RP1210Interface class with an API name that doesn't exist.
    """
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - (Vendor Name Missing) - (drivers invalid)"
    assert rp1210.getAPI() == RP1210.RP1210API(api_name, None) 
    assert rp1210.isValid() == False
    assert rp1210.getAPIName() == api_name
    assert rp1210.getName() == "(Vendor Name Missing)"
    assert rp1210.getAddress1() == ""
    assert rp1210.getAddress2() == ""
    assert rp1210.getCity() == ""
    assert rp1210.getState() == ""
    assert rp1210.getCountry() == ""
    assert rp1210.getPostal() == ""
    assert rp1210.getTelephone() == ""
    assert rp1210.getFax() == ""
    assert rp1210.getVendorURL() == ""
    assert rp1210.getVersion() == ""
    assert rp1210.autoDetectCapable() == False
    assert rp1210.getCANAutoBaud() == False
    assert rp1210.getTimeStampWeight() == 1.0
    assert rp1210.getMessageString() == ""
    assert rp1210.getErrorString() == ""
    assert rp1210.getRP1210Version() == ""
    assert rp1210.getDebugLevel() == -1
    assert rp1210.getDebugFile() == ""
    assert rp1210.getDebugMode() == -1
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == []
    assert rp1210.getJ1939FormatsSupported() == []
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolNames() == []
    assert rp1210.getProtocolIDs() == []
    assert rp1210.getName() == rp1210.getDescription()

def test_InvalidAPIName_Devices_Protocols():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolIDs() == []
    assert rp1210.getProtocol() == None
    assert rp1210.getProtocol(3) == None
    assert rp1210.getDevice(3) == None

def test_Invalid_Device():
    device = RP1210.RP1210Device(None)
    assert device.getID() == -1
    assert device.getDescription() == ""
    assert device.getName() == ""
    assert device.getParams() == ""
    assert device.getMultiCANChannels() == 0
    assert device.getMultiJ1939Channels() == 0
    assert str(device) == "(Invalid Device)"

def test_Invalid_Protocol():
    protocol = RP1210.RP1210Protocol(None)
    assert protocol.getDescription() == ""
    assert protocol.getSpeed() == []
    assert protocol.getString() == ""
    assert protocol.getParams() == ""
    assert protocol.getDevices() == []
    assert str(protocol) == " - "

def test_InvalidAPIName_load_dll():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.api.getDLL() == None
    assert rp1210.api.isValid() == False

def test_InvalidAPIName_conforms_to_rp1210C():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.api.conformsToRP1210C() == False

def test_sanitize_msg_param_bytes():
    assert sanitize_msg_param(b'0') == b'0'
    assert sanitize_msg_param(b'\x00') == b'\x00'
    assert sanitize_msg_param(b'16') == b'16'
    assert sanitize_msg_param(b'\x10') == b'\x10'
    assert sanitize_msg_param(b'0', 2) == b'\x000'
    assert sanitize_msg_param(b'\x00', 2) == b'\x00\x00'
    assert sanitize_msg_param(b'') == b''
    assert sanitize_msg_param(b'', 4) == b'\x00\x00\x00\x00'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A') == b'\x43\x64\xFE\x4A'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A', 3) == b'\x43\x64\xFE'
    assert sanitize_msg_param(b'\x43\x64\xFE\x4A', 3, 'little') == b'\x4A\xFE\x64'
    assert sanitize_msg_param(b'\x00\x00\x00') == b'\x00\x00\x00'
    assert sanitize_msg_param(b'\xFF\xFF\xFF') == b'\xFF\xFF\xFF'
    assert sanitize_msg_param(b'\xFF\xFF\xFF', 1) == b'\xFF'
    assert sanitize_msg_param(b'\x01\x02\x03', 1) == b'\x01'
    assert sanitize_msg_param(b'\x01\x02\x03', 1, 'little') == b'\x03'
    
def test_sanitize_msg_param_str():
     assert sanitize_msg_param("0") == b'0'
     assert sanitize_msg_param("16") == b'16'
     assert sanitize_msg_param("0", 2) == b'\x000'
     assert sanitize_msg_param("") == b''
     assert sanitize_msg_param("", 4) == b'\x00\x00\x00\x00'
     assert sanitize_msg_param("Boogity") == b"Boogity"
     assert sanitize_msg_param("Boogity", 4, 'little') == b'ytig'

def test_sanitize_msg_param_int():
    assert sanitize_msg_param(0) == b'\x00'
    assert sanitize_msg_param(16) == b'\x10'
    assert sanitize_msg_param(0x10) == b'\x10'
    assert sanitize_msg_param(0, 2) == b'\x00\x00'
    assert sanitize_msg_param(0xDEADBEEF, 4, 'little') == b'\xEF\xBE\xAD\xDE'
    assert sanitize_msg_param(0xDEADBEEF, 4, 'big') == b'\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(0xDEADBEEF, 4) == b'\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(0xDEADBEEFEE, 5) == b'\xDE\xAD\xBE\xEF\xEE'
    assert sanitize_msg_param(0xDEADBEEF, 6, 'little') == b'\xEF\xBE\xAD\xDE\x00\x00'
    assert sanitize_msg_param(0xDEADBEEF, 6, 'big') == b'\x00\x00\xDE\xAD\xBE\xEF'
    assert sanitize_msg_param(1234567) == b'\x12\xD6\x87'
    assert sanitize_msg_param(0x12345) == b'\x01\x23\x45'
    for x in range(0, 0xFFFF):
        assert x == int.from_bytes(sanitize_msg_param(x), 'big')
        assert x == int.from_bytes(sanitize_msg_param(x, 2, 'little'), 'little')

def test_sanitize_msg_param_bool():
    assert sanitize_msg_param(True, 1) == b'\x01'
    assert sanitize_msg_param(False, 1) == b'\x00'
    assert sanitize_msg_param(True, 2) == b'\x00\x01'
    assert sanitize_msg_param(False, 2) == b'\x00\x00'
    assert sanitize_msg_param(True, 2, 'little') == b'\x01\x00'
    assert sanitize_msg_param(True) == b'\x01'
    assert sanitize_msg_param(False) == b'\x00'

def test_sanitize_msg_param_float():
    assert sanitize_msg_param(0.34) == b'\x00'

def test_sanitize_msg_param_typeerror():
    with pytest.raises(TypeError):
        sanitize_msg_param(RP1210.RP1210VendorList())
        sanitize_msg_param(CDLL())

def test_rp1210client_populate_logic():
    """Tests whether RP1210Client recognizes relevant drivers when adapter is disconnected."""
    vendors = []
    vendors.clear()
    api_list = RP1210.getAPINames(RP121032_PATH)
    if api_list == []:
        pytest.xfail("RP121032.ini not installed on system; calling XFAIL")
    try:
        for api_name in api_list:
            try:
                vendors.append(RP1210.RP1210Config(api_name))
            except Exception as err:
                # skip this API if its .ini file can't be parsed
                print(err)
                pass
    except Exception as err:
        print(err)
        vendors = []
    assert vendors != []

@pytest.mark.parametrize("input,expected",[
    (0, 0), (1, 1), (2, 2), (-1, 1), (-2, 2), (128, 128), (-128, 128), (0x10FA3, 0x0FA3),
    (-0x10FA3, 0x0FA3), (0xFFFF, 0), (0xFFFE, 1), (0xFFFD, 2), (-0xFFFD, 2), (-0xFFFFD, 2)
])
def test_driver_clientid_fix(input, expected):
    """Tests _driver_clientid_fix function in RP1210API."""
    class TestAPI(RP1210.RP1210API): # gotta make _driver_clientid_fix public
        def __init__(self, api_name: str, WorkingAPIDirectory: str = None) -> None:
            super().__init__(api_name, WorkingAPIDirectory)
    
        def fix(self, val : int):
            return self._validate_and_fix_clientid(val)

    api = TestAPI("test")
    assert api.fix(input) == expected

@pytest.mark.parametrize("input,expected",[
    (114, 129), (0,0), (-0xFFFF, 0), (-0xFFFE, 1)
])
def test_driver_clientid_fix_PEAKRP32(input, expected):
    """Tests _driver_clientid_fix function in RP1210API when using PEAKRP32 API."""
    class TestAPI(RP1210.RP1210API):
        def __init__(self, api_name: str, WorkingAPIDirectory: str = None) -> None:
            super().__init__(api_name, WorkingAPIDirectory)
    
        def fix(self, val : int):
            return self._validate_and_fix_clientid(val)

    api = TestAPI("PEAKRP32")
    assert api.fix(input) == expected

def test_RP1210Client_magic_methods():
    """Test __str__ and __int__  in RP1210Client."""
    client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    for vendor in client:
        client.setVendor(vendor)
        assert str(client) == client.getCurrentVendor().getName()
    assert int(client) == client.clientID

def test_RP1210Protocol_magic_methods_arbitrary():
    """Test __bool__ in RP1210Protocol"""
    protocol = RP1210.RP1210Protocol({})
    assert bool(protocol) == bool({})
    protocol = RP1210.RP1210Protocol({'test':'1'})
    assert bool(protocol) == bool({'test':'1'})

def test_RP1210Device_magic_methods_arbitrary():
    """Test __bool__ in RP1210Device"""
    device = RP1210.RP1210Device({})
    assert not device
    assert "Invalid" in str(device)
    assert int(device) == -1
    device2 = RP1210.RP1210Device({'test':'1'})
    assert not device2
    assert "Invalid" in str(device2)
    assert int(device2) == -1
    assert device != device2

def test_RP1210VendorList_setDeviceByDeviceID():
    """Access `device` property in RP1210VendorList."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    for vendor in vendors:
        vendors.setVendor(vendor)
        for deviceID in vendor.getDeviceIDs():
            vendors.setDevice(deviceID)
            assert vendors.device == vendors.getCurrentDevice()
            vendors.device = deviceID
            assert vendors.device == vendors.getCurrentDevice()
        
def test_RP1210VendorList_setDeviceByDevice():
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    for vendor in vendors:
        vendors.setVendor(vendor)
        for deviceID in vendor.getDevices():
            vendors.device = deviceID
            assert vendors.device == vendors.getCurrentDevice()
        for device in vendor.getDevices():
            vendors.setDevice(device)
            assert vendors.device == vendors.getCurrentDevice()

def test_RP1210VendorList_setDevice_Error():
    """Invalid cases of setDevice"""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    for vendor in vendors:
        vendors.setVendor(vendor)
        with pytest.raises(TypeError):
            vendors.device = "dinglebop"


# Tets that specifically acheive 100% branch coverge (while sometimes being non-sensyical for this application)

class Test_translateErrorCode:
    @pytest.mark.parametrize("input, output", [
        ('abc', 'abc'),
        (-1, 'NO_ERRORS'),
        (0, 'NO_ERRORS'),
        (1, 'NO_ERRORS'),
        (127, 'NO_ERRORS'),
        (128, 'ERR_DLL_NOT_INITIALIZED'),
        (0x8000, '32768'),
        (0x8001, '32766'),
        (0xFFFF - 128, "ERR_DLL_NOT_INITIALIZED"),
        (-128, "ERR_DLL_NOT_INITIALIZED"),
        (0x48FFFFF, "NO_ERRORS"),
        (0x48FFF7F, "ERR_DLL_NOT_INITIALIZED"),
        ("chungus",  "chungus"),
    ])
    def test_translateErrorCode_edge_cases(self, input, output):
        assert output == RP1210.translateErrorCode(input)

    def test_translateErrorCode_all_errors(self):
        for i in range(0, 1000):
            if i in RP1210.RP1210_ERRORS:
                assert RP1210.RP1210_ERRORS[i] == RP1210.translateErrorCode(i)
            else:
                if i < 128:
                    assert 'NO_ERRORS' == RP1210.translateErrorCode(i)
                else: 
                    assert str(i) == RP1210.translateErrorCode(i)

class Test_getAPINames:
    def test_getAPINames_notfound(self):
        """test getAPINames when file doesn't exist at path"""
        with pytest.raises(FileNotFoundError):
            path = "doesnt_exist.ini"
            assert [] == RP1210.getAPINames(path)

    def test_getAPINames_empty(self):
        """generate empty file and provide its path to getAPINames"""
        # generate file
        path = "getAPINames_empty.ini"
        create_file(path)
        # test output
        assert [] == RP1210.getAPINames(path)

    def test_getAPINames_invalid(self):
        """generate an invalid file and provide its path to getAPINames"""
        # generate file
        path = "getAPINames_invalid.ini"
        parser = create_file(path)
        parser.add_section("[")
        with open(path, 'w') as file:
            parser.write(file)
        # test output
        assert [] == RP1210.getAPINames(path)

    def test_getAPINames_default(self):
        assert ['PEAKRP32', 'DLAUSB32', 'NULN2R32', 'DG121032', 'VRP32'] == RP1210.getAPINames()

def test_delete_files():
    """Deletes the files created by other tests."""
    assert os.path.exists("getAPINames_empty.ini")
    delete_file("getAPINames_empty.ini")
    assert not os.path.exists("getAPINames_empty.ini")
    
    assert os.path.exists("getAPINames_invalid.ini")
    delete_file("getAPINames_invalid.ini")
    assert not os.path.exists("getAPINames_invalid.ini")

class Test_RP1210Protocol:
    def test_RP1210Protocol_init(self):
        protocol = RP1210.RP1210Protocol({})
        assert {} == protocol.contents
        protocol = RP1210.RP1210Protocol({1: 2})
        assert {1: 2} == protocol.contents

    def test_RP1210Protocol_str(self):
        protocol = RP1210.RP1210Protocol({})
        assert " - " == str(protocol)

        protocol = RP1210.RP1210Protocol({
            "ProtocolString": "foo",
        })
        assert "foo - " == str(protocol)

        protocol = RP1210.RP1210Protocol({
            "ProtocolDescription": "bar",
        })
        assert " - bar" == str(protocol)

        protocol = RP1210.RP1210Protocol({
            "ProtocolString": "foo",
            "ProtocolDescription": "bar",
        })
        assert "foo - bar" == str(protocol)

    def test_RP1210Protocol_eq(self):
        protocol = RP1210.RP1210Protocol({})
        protocol1 = RP1210.RP1210Protocol({})
        
        with pytest.raises(TypeError):
            same = protocol == 0

        assert protocol == protocol1

        protocol1 = RP1210.RP1210Protocol({0: 0})
        assert protocol != protocol1

    def test_RP1210Protocol_bool(self):
        protocol = RP1210.RP1210Protocol({})
        assert not bool(protocol)
        protocol = RP1210.RP1210Protocol({0: 0})
        assert bool(protocol)

    def test_RP1210Protocol_getDescription(self):
        protocol = RP1210.RP1210Protocol({})
        assert '' == protocol.getDescription()
        protocol = RP1210.RP1210Protocol({'ProtocolDescription': 'foo'})
        assert 'foo' == protocol.getDescription()

    def test_RP1210Protocol_getSpeed(self):
        protocol = RP1210.RP1210Protocol({})
        assert [] == protocol.getSpeed()
        protocol = RP1210.RP1210Protocol({'ProtocolSpeed': 'foo'})
        assert ['foo'] == protocol.getSpeed()
        protocol = RP1210.RP1210Protocol({'ProtocolSpeed': 'foo,bar,baz'})
        assert ['foo', 'bar', 'baz'] == protocol.getSpeed()

    def test_RP1210Protocol_getString(self):
        protocol = RP1210.RP1210Protocol({})
        assert '' == protocol.getString()
        protocol = RP1210.RP1210Protocol({'ProtocolString': 'foo'})
        assert 'foo' == protocol.getString()

    def test_RP1210Protocol_getParams(self):
        protocol = RP1210.RP1210Protocol({})
        assert '' == protocol.getParams()
        protocol = RP1210.RP1210Protocol({'ProtocolParams': 'foo'})
        assert 'foo' == protocol.getParams()

    def test_RP1210Protocol_getDevices(self):
        protocol = RP1210.RP1210Protocol({})
        assert [] == protocol.getDevices()
        protocol = RP1210.RP1210Protocol({'Devices': 'foo'})
        assert [] == protocol.getDevices()
        protocol = RP1210.RP1210Protocol({'Devices': '1'})
        assert [1] == protocol.getDevices()
        protocol = RP1210.RP1210Protocol({'Devices': '1,2,3,4'})
        assert [1, 2, 3, 4] == protocol.getDevices()
        protocol = RP1210.RP1210Protocol({'Devices': '1,2,3,4,foo'})
        assert [] == protocol.getDevices()

class Test_RP1210Device:
    def test_RP1210Device_init(self):
        device = RP1210.RP1210Device({})
        assert {} == device.contents
        device = RP1210.RP1210Device({1: 2})
        assert {1: 2} == device.contents

    def test_RP1210Device_str(self):
        device = RP1210.RP1210Device({})
        assert '(Invalid Device)' == str(device)
        device = RP1210.RP1210Device({'DeviceID': 0})
        assert '0' == str(device)
        device = RP1210.RP1210Device({'DeviceID': 0, 'DeviceDescription': 'bar'})
        assert '0 - bar' == str(device)

    def test_RP1210Device_eq(self):
        device = RP1210.RP1210Device({})
        device1 = RP1210.RP1210Device({})
        
        with pytest.raises(TypeError):
            same = device == 0

        assert device == device1

        device1 = RP1210.RP1210Device({0: 0})
        assert device != device1

    def test_RP1210Device_bool(self):
        device = RP1210.RP1210Device({})
        assert not bool(device)
        device = RP1210.RP1210Device({'DeviceID': -1})
        assert not bool(device)
        device = RP1210.RP1210Device({'DeviceID': 0})
        assert bool(device)
        device = RP1210.RP1210Device({'DeviceID': 1})
        assert bool(device)

    def test_RP1210Device_int(self):
        device = RP1210.RP1210Device({})
        assert -1 == int(device)
        device = RP1210.RP1210Device({'DeviceID': -1})
        assert -1 == int(device)
        device = RP1210.RP1210Device({'DeviceID': 0})
        assert 0 == int(device)
        device = RP1210.RP1210Device({'DeviceID': 1})
        assert 1 == int(device)

    def test_RP1210Device_getID(self):
        device = RP1210.RP1210Device({})
        assert -1 == device.getID()
        device = RP1210.RP1210Device({'DeviceID': 'foo'})
        assert -1 == device.getID()
        device = RP1210.RP1210Device({'DeviceID': -1})
        assert -1 == device.getID()
        device = RP1210.RP1210Device({'DeviceID': 0})
        assert 0 == device.getID()
        device = RP1210.RP1210Device({'DeviceID': 1})
        assert 1 == device.getID()

    def test_RP1210Device_getDescription(self):
        device = RP1210.RP1210Device({})
        assert '' == device.getDescription()
        device = RP1210.RP1210Device({'DeviceDescription': 'foo'})
        assert 'foo' == device.getDescription()

    def test_RP1210Device_getName(self):
        device = RP1210.RP1210Device({})
        assert '' == device.getName()
        device = RP1210.RP1210Device({'DeviceName': 'foo'})
        assert 'foo' == device.getName()

    def test_RP1210Device_getParams(self):
        device = RP1210.RP1210Device({})
        assert '' == device.getParams()
        device = RP1210.RP1210Device({'DeviceParams': 'foo'})
        assert 'foo' == device.getParams()

    def test_RP1210Device_getMultiCANChannels(self):
        device = RP1210.RP1210Device({})
        assert 0 == device.getMultiCANChannels()
        device = RP1210.RP1210Device({'MultiCANChannels': 'foo'})
        assert 0 == device.getMultiCANChannels()
        device = RP1210.RP1210Device({'MultiCANChannels': '1'})
        assert 1 == device.getMultiCANChannels()
        device = RP1210.RP1210Device({'MultiCANChannels': '-1'})
        assert -1 == device.getMultiCANChannels()

    def test_RP1210Device_getMultiJ1939Channels(self):
        device = RP1210.RP1210Device({})
        assert 0 == device.getMultiJ1939Channels()
        device = RP1210.RP1210Device({'MultiJ1939Channels': 'foo'})
        assert 0 == device.getMultiJ1939Channels()
        device = RP1210.RP1210Device({'MultiJ1939Channels': '1'})
        assert 1 == device.getMultiJ1939Channels()
        device = RP1210.RP1210Device({'MultiJ1939Channels': '-1'})
        assert -1 == device.getMultiJ1939Channels()

class Test_RP1210Config:
    def test_RP1210Config_init(self):
        config = RP1210.RP1210Config(api_name='')
        assert '' == config._api_name
        assert False == config._api_valid
        assert RP1210.RP1210API('', None) == config.api
        assert None == config._configDir

        config = RP1210.RP1210Config(api_name='PEAKRP32')
        assert 'PEAKRP32' == config._api_name
        assert True == config._api_valid
        assert RP1210.RP1210API('PEAKRP32', None) == config.api
        assert None == config._configDir

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path='foo')
        assert 'PEAKRP32' == config._api_name
        assert False == config._api_valid
        assert RP1210.RP1210API('PEAKRP32', None) == config.api
        assert 'foo' == config._configDir

    def test_RP1210Config_str(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert ' - (Vendor Name Missing) - (drivers invalid)' == str(config)
        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PEAKRP32 - PEAK-System PCAN Adapter' == str(config)
        config = RP1210.RP1210Config(api_name='DLAUSB32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'DLAUSB32 - Noregon Systems Inc., DLA+ 2.0 Adapter' == str(config)

    def test_RP1210Config_bool(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == bool(config)
        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == bool(config)

    def test_RP1210Config_eq(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        config1 = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        
        assert config == config1
        assert ' - (Vendor Name Missing) - (drivers invalid)' == config

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert config != config1
        assert config == 'PEAKRP32 - PEAK-System PCAN Adapter'
        config1 = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert config == config1

    def test_RP1210Config_getApi(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert RP1210.RP1210API('', None) == config.getAPI()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert RP1210.RP1210API('PEAKRP32', None) == config.getAPI()

    def test_RP1210Config_getIsValid(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.isValid()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == config.isValid()

    def test_RP1210Config_getAPIName(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getAPIName()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PEAKRP32' == config.getAPIName()

    def test_RP1210Config_getName(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '(Vendor Name Missing)' == config.getName()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PEAK-System PCAN Adapter' == config.getName()

    def test_RP1210Config_getDescription(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '(Vendor Name Missing)' == config.getDescription()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PEAK-System PCAN Adapter' == config.getDescription()

    def test_RP1210Config_getAddress1(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getAddress1()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'Otto-Roehm str. 69' == config.getAddress1()

    def test_RP1210Config_getAddress2(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getAddress2()

        config = RP1210.RP1210Config(api_name='DGDPA5MA', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '33604 West 8 Mile Road' == config.getAddress2()

    def test_RP1210Config_getCity(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getCity()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'Darmstadt' == config.getCity()

    def test_RP1210Config_getState(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getState()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'Hessen' == config.getState()

    def test_RP1210Config_getCountry(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getCountry()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'Germany' == config.getCountry()

    def test_RP1210Config_getPostal(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getPostal()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '64293' == config.getPostal()

    def test_RP1210Config_getTelephone(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getTelephone()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '0049-6151-817320' == config.getTelephone()

    def test_RP1210Config_getFax(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getFax()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '0049-6151-817329' == config.getFax()

    def test_RP1210Config_getVendorURL(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getVendorURL()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'http://www.peak-system.com' == config.getVendorURL()

    def test_RP1210Config_getVersion(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getVersion()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '3.0' == config.getVersion()

    def test_RP1210Config_getAutoDetectCapable(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.getAutoDetectCapable()

        # exception handling
        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.getAutoDetectCapable()

        config = RP1210.RP1210Config(api_name='NULN2R32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == config.getAutoDetectCapable()

    def test_RP1210Config_autoDetectCapable(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.autoDetectCapable()

        config = RP1210.RP1210Config(api_name='NULN2R32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == config.autoDetectCapable()

    def test_RP1210Config_getTimeStampWeight(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1.0 == config.getTimeStampWeight()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1.0 == config.getTimeStampWeight()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1000.0 == config.getTimeStampWeight()

    def test_RP1210Config_getMessageString(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getMessageString()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PCANRP32_MSG' == config.getMessageString()

    def test_RP1210Config_getErrorString(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getErrorString()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'PCANRP32_ERR' == config.getErrorString()

    def test_RP1210Config_getRP1210Version(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getRP1210Version()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 'C' == config.getRP1210Version()

    def test_RP1210Config_getDebugLevel(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert -1 == config.getDebugLevel()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert -1 == config.getDebugLevel()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 0 == config.getDebugLevel()

    def test_RP1210Config_getDebugFile(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '' == config.getDebugFile()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        # asserting that the abspaths are the same because...
        # if you do a string compare, \P in the hardcoded result gives a warning in the test
        assert os.path.abspath('c:/PEAK_RP1210_Debug.txt') == os.path.abspath(config.getDebugFile())

    def test_RP1210Config_getDebugMode(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert -1 == config.getDebugMode()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert -1 == config.getDebugMode()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1 == config.getDebugMode()

    def test_RP1210Config_getDebugFileSize(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1024 == config.getDebugFileSize()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1024 == config.getDebugFileSize()

        config = RP1210.RP1210Config(api_name='DrewLinQ', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 2048 == config.getDebugFileSize()

    def test_RP1210Config_getNumberOfSessions(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1 == config.getNumberOfSessions()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 1 == config.getNumberOfSessions()

        config = RP1210.RP1210Config(api_name='DTKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert 8 == config.getNumberOfSessions()

    def test_RP1210Config_getCANFormatsSupported(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getCANFormatsSupported()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getCANFormatsSupported()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [3, 4, 5] == config.getCANFormatsSupported()

    def test_RP1210Config_getJ1939FormatsSupported(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getJ1939FormatsSupported()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getJ1939FormatsSupported()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [1, 2, 5] == config.getJ1939FormatsSupported()

    def test_RP1210Config_getCANAutoBaud(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.getCANAutoBaud()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.getCANAutoBaud()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == config.getCANAutoBaud()

    def test_RP1210Config_autoBaudEnabled(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config.autoBaudEnabled()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert True == config.autoBaudEnabled()

    def test_RP1210Config_getDevice(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getDevice(0)

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getDevice(0)

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getDevice(0)

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        device = config.getDevice(1)
        device2 = RP1210.RP1210Device({
            'DeviceID': 1,
            'DeviceDescription': 'PEAK-System CAN Adapter (USB, 1 Channel)',
            'DeviceName': 'PCAN-USB',
            'DeviceParams': '{device=pcan_usb,hardwaretype=0x201,deviceid=255,partnumber=IPEH-002021/002022}',
            'MultiCANChannels': 1,
            'MultiJ1939Channels': 1,
            'MultiISO15765Channels': 1,
        })
        assert device2.getDescription() == device.getDescription()
        assert device2.getID() == device.getID()
        assert device2.getMultiCANChannels() == device.getMultiCANChannels()
        assert device2.getName() == device.getName()
        assert device2.getParams() == device.getParams()

    def test_RP1210Config_getDevices(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getDevices()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getDevices()

        config = RP1210.RP1210Config(api_name='CIL7R32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        devices = config.getDevices()
        assert devices
        assert len(devices) == 3
        for device in devices:
            assert isinstance(device, RP1210.RP1210Device)

    @patch.object(RP1210.RP1210Config, 'getDeviceIDs')
    def test_RP1210Config_getDevices_exception(self, patch_fn):
        config = RP1210.RP1210Config(api_name='CIL7R32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        patch_fn.return_value = 2 # causes exception because RP1210.RP1210Config.getDeviceIDs returns an int when called when a list was expected
        assert [] == config.getDevices()

    def test_RP1210Config_getProtocol(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getProtocol()

        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getProtocol(0)

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getProtocol()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getProtocol(0)

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert None == config.getProtocol(0)

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        protocol = config.getProtocol()
        protocol2 = RP1210.RP1210Protocol({
            'ProtocolString': 'J1939',
            'ProtocolDescription': 'SAE J1939 Protocol',
            'ProtocolSpeed': '125,250,500,1000,Auto',
            'ProtocolParams': '',
            'Devices': '1',
        })
        assert protocol2.getDescription() == protocol.getDescription()
        assert protocol2.getDevices() == protocol.getDevices()
        assert protocol2.getParams() == protocol.getParams()
        assert protocol2.getSpeed() == protocol.getSpeed()
        assert protocol2.getString() == protocol.getString()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        protocol = config.getProtocol(10)
        protocol2 = RP1210.RP1210Protocol({
            'ProtocolString': 'CAN',
            'ProtocolDescription': 'CAN Network Protocol',
            'ProtocolSpeed': '125,250,500,1000,Auto',
            'ProtocolParams': '',
            'Devices': '1',
        })
        assert protocol2.getDescription() == protocol.getDescription()
        assert protocol2.getDevices() == protocol.getDevices()
        assert protocol2.getParams() == protocol.getParams()
        assert protocol2.getSpeed() == protocol.getSpeed()
        assert protocol2.getString() == protocol.getString()

    def test_RP1210Config_getProtocols(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocols()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocols()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        protocols = config.getProtocols()        
        assert protocols
        assert len(protocols) == 3
        for protocol in protocols:
            assert isinstance(protocol, RP1210.RP1210Protocol)

    @patch.object(RP1210.RP1210Config, 'getProtocolNames')
    def test_RP1210Config_getProtocols_exception(self, patch_fn):
        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        patch_fn.return_value = 2 # causes exception because RP1210.RP1210Config.getProtocolNames returns an int when called when a list was expected
        assert [] == config.getProtocols()

    def test_RP1210Config_getProtocolNames(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocolNames()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocolNames()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert ['CAN', 'J1939', 'ISO15765'] == config.getProtocolNames()

    @patch.object(RP1210.RP1210Config, 'getProtocolIDs')
    def test_RP1210Config_getProtocolNames_exception(self, patch_fn):
        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        patch_fn.return_value = 2 # causes exception because RP1210.RP1210Config.getProtocolIDs returns an int when called when a list was expected
        assert [] == config.getProtocolNames()

    def test_RP1210Config_getProtocolIDs(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocolIDs()

        config = RP1210.RP1210Config(api_name='invalid_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [] == config.getProtocolIDs()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert [10, 20, 30] == config.getProtocolIDs()

    def test_RP1210Config_populate(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config._api_valid

        config = RP1210.RP1210Config(api_name='extra_empty_api', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert False == config._api_valid
        config._api_valid = True
        assert True == config._api_valid
        config.populate()
        assert False == config._api_valid

    def test_RP1210Config_getPath(self):
        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=None)
        # asserting that the abspaths are the same because...
        # if you do a string compare, \P in the hardcoded result gives a warning in the test
        assert os.path.abspath('C:/Windows/.ini') == os.path.abspath(config.getPath())

        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '.\\Test\\test-files\\ini-files\\.ini' in config.getPath()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY)
        assert '.\\Test\\test-files\\ini-files\\PEAKRP32.ini' in config.getPath()

        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path=INI_DIRECTORY + '\\PEAKRP32.ini')
        assert '.\\Test\\test-files\\ini-files\\PEAKRP32.ini' in config.getPath()

        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path='.\\Test\\test-files\\ini-files\\PEAKRP32.ini')
        assert '.\\Test\\test-files\\ini-files\\PEAKRP32.ini' in config.getPath()

        config = RP1210.RP1210Config(api_name='', api_path=DLL_DIRECTORY, config_path='Test\\test-files\\ini-files\\')
        assert '.\\Test\\test-files\\ini-files\\.ini' in config.getPath()

        config = RP1210.RP1210Config(api_name='PEAKRP32', api_path=DLL_DIRECTORY, config_path='Test\\test-files\\ini-files\\')
        assert '.\\Test\\test-files\\ini-files\\PEAKRP32.ini' in config.getPath()

class Test_RP1210API:
    def test_RP1210API_init(self):
        api = RP1210.RP1210API(api_name='')
        assert False == api._api_valid
        assert '' == api._api_name
        assert None == api.dll
        assert True == api._conforms_to_rp1210c
        assert None  == api._libDir

        api = RP1210.RP1210API(api_name='foo', WorkingAPIDirectory='bar')
        assert False == api._api_valid
        assert 'foo' == api._api_name
        assert None == api.dll
        assert True == api._conforms_to_rp1210c
        assert 'bar'  == api._libDir

    def test_RP1210API_bool(self):
        api = RP1210.RP1210API(api_name='')
        assert False == bool(api)
        
        assert False == api._api_valid
        api._api_valid = True
        api.dll = True
        assert True == api._api_valid
        assert True == api.dll

        assert True  == bool(api)

    def test_RP1210API_str(self):
        api = RP1210.RP1210API(api_name='')
        assert '' == str(api)

        api = RP1210.RP1210API(api_name='foo', WorkingAPIDirectory='bar')
        assert 'foo' == str(api)

    def test_RP1210API_eq(self):
        api1 = RP1210.RP1210API(api_name='foo')
        api2 = RP1210.RP1210API(api_name='bar')
        api3 = RP1210.RP1210API(api_name='foo')
        api4 = RP1210.RP1210API(api_name='bar')

        assert api1 == api1
        assert api1 == api3
        assert api1 != api2
        assert api1 != api4
        assert api1 == 'foo'

    def test_RP1210API_getAPIName(self):
        api = RP1210.RP1210API(api_name='')
        assert '' == api.getAPIName()

        api = RP1210.RP1210API(api_name='foo', WorkingAPIDirectory='bar')
        assert 'foo' == api.getAPIName()

    def test_RP1210API_loadDLL(self):
        api = RP1210.RP1210API(api_name='')
        api._api_valid = True
        api.loadDLL()
        assert False == api._api_valid
        assert not api.dll

        api = RP1210.RP1210API(api_name='PEAKRP32')
        api._api_valid = False
        api.loadDLL()
        assert True == api._api_valid
        assert api.dll

        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory='foo')
        api.loadDLL()
        assert False == api._api_valid
        assert not api.dll

        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.abspath('Test/test-files/dlls/'))
        api.loadDLL()
        assert True == api._api_valid
        assert api.dll

        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.relpath('Test/test-files/dlls/'))
        api.loadDLL()
        assert True == api._api_valid
        assert api.dll

    def test_RP1210API_isValid(self):
        api = RP1210.RP1210API(api_name='')
        assert False == api.isValid()

        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.abspath('Test/test-files/dlls/'))
        assert True == api.isValid()

    def test_RP1210API_conformsToRP1210C(self):
        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.abspath('Test/test-files/dlls/'))
        assert True == api.isValid()

        api._conforms_to_rp1210c  = True
        assert True == api._conforms_to_rp1210c

        assert True == api.conformsToRP1210C() # conforms and is valid

        api._conforms_to_rp1210c  = False
        assert False == api._conforms_to_rp1210c

        assert False == api.conformsToRP1210C() # no conform and valid
        
        api = RP1210.RP1210API(api_name='')
        assert False == api.isValid()

        api._conforms_to_rp1210c  = True
        assert True == api._conforms_to_rp1210c

        assert False == api.conformsToRP1210C() # conforms and no valid

        api._conforms_to_rp1210c  = False
        assert False == api._conforms_to_rp1210c

        assert False == api.conformsToRP1210C() # no conforms and no valid

    def test_RP1210API_setDLL(self):
        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.abspath('Test/test-files/dlls/'))
        dll = cdll.LoadLibrary(os.path.abspath('Test/test-files/dlls/PEAKRP32.dll'))
        api.setDLL(dll)
        assert True == api._api_valid
        api.setDLL(None)
        assert False == api._api_valid

    @patch.object(RP1210.RP1210API, '_init_functions')
    def test_RP1210API_setDLL_exception(self, patch_fn):
        api = RP1210.RP1210API(api_name='PEAKRP32', WorkingAPIDirectory=os.path.abspath('Test/test-files/dlls/'))
        dll = cdll.LoadLibrary(os.path.abspath('Test/test-files/dlls/PEAKRP32.dll'))
        api.setDLL(dll)
        assert True == api._api_valid
        patch_fn.side_effect = OSError # cause OSError to enter except block
        api.setDLL(dll)
        assert False == api._api_valid

    def test_RP1210API_ClientConnect(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 129 == api.ClientConnect(0)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 129 == api.ClientConnect(1)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 129 == api.ClientConnect(10)

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert 134 == api.ClientConnect(0)

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert 134 == api.ClientConnect(1)

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert 134 == api.ClientConnect(10)

    def test_RP1210API_ClientDisconnect(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.ClientConnect(0)
        assert 129 == api.ClientDisconnect(0)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.ClientConnect(1)
        assert 129 == api.ClientDisconnect(1)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.ClientConnect(10)
        assert 129 == api.ClientDisconnect(10)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(0)
        assert 128 == api.ClientDisconnect(0)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(1)
        assert 128 == api.ClientDisconnect(1)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(10)
        assert 128 == api.ClientDisconnect(10)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(0)
        assert 128 == api.ClientDisconnect(1)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(1)
        assert 128 == api.ClientDisconnect(0)

        api = RP1210.RP1210API(api_name='NULN2R32')
        api.ClientConnect(10)
        assert 128 == api.ClientDisconnect(0)

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert 128 == api.ClientDisconnect(0)
        api.ClientConnect(10)
        
    def test_RP1210API_SendMessage(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 129 == api.SendMessage(0, 0)

        # force the return value of the RP1210_SendMessage command :)
        def dummy(a, b, c, d, e):
            return 0xFFFFFF

        api.dll.RP1210_SendMessage = dummy
        assert -1 == api.SendMessage(0, 0)
    
    def test_RP1210API_ReadMessage(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert -129 == api.ReadMessage(0, b'\xff\xff\xff')

        # force the return value of the RP1210_SendMessage command :)
        def dummy(a, b, c, d):
            return 0xFFFFFF

        api.dll.RP1210_ReadMessage = dummy
        assert -1 == api.ReadMessage(0, b'\xff\xff\xff')

    def test_RP1210API_ReadDirect(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert b'' == api.ReadDirect(0)

    @patch.object(RP1210.RP1210API, 'ReadMessage')
    def test_RP1210API_ReadDirect_size_gt_0(self, patch_fn):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        patch_fn.return_value = 1
        assert b'\x00' == api.ReadDirect(0)

    # Running these ReadVersion tests with all test files causes these tests, and tests in j1939 to fail
    # The tests pass when run by themselves. They are disabled now to not cause breakeages
    # Thes failures are liekly caused by shared recources being accessed in the tests

    def DIABLED_test_RP1210API_ReadVersion(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 65535 == api.ReadVersion(b'', b'', b'', b'')

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert 51 == api.ReadVersion(b'', b'', b'', b'')

    def DIABLED_test_RP1210API_ReadVersionDirect(self):
        api = RP1210.RP1210API(api_name='DLAUSB32')
        assert ('4.1', '4.0') == api.ReadVersionDirect()

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert ('1.0', '3.0') == api.ReadVersionDirect()

    def DIABLED_test_RP1210API_ReadDLLVersion(self):
        api = RP1210.RP1210API(api_name='DLAUSB32')
        assert '4.1' == api.ReadDLLVersion()

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert '1.0' == api.ReadDLLVersion()

    def DIABLED_test_RP1210API_ReadAPIVersion(self):
        api = RP1210.RP1210API(api_name='DLAUSB32')
        assert '4.0' == api.ReadAPIVersion()

        api = RP1210.RP1210API(api_name='NULN2R32')
        assert '3.0' == api.ReadAPIVersion()

    def test_RP1210API_ReadDetailedVersion(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()
        assert True == api._conforms_to_rp1210c

        def dummy(a, b, c, d):
            return 69420

        api.dll.RP1210_ReadDetailedVersion = dummy

        assert 69420 == api.ReadDetailedVersion(0, b'', b'', b'')

        api._conforms_to_rp1210c = False
        assert False == api._conforms_to_rp1210c

        assert 128 == api.ReadDetailedVersion(0, b'', b'', b'')

    def test_RP1210API_ReadDetailedVersionDirect(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()
        api._conforms_to_rp1210c = False
        assert False == api._conforms_to_rp1210c

        assert ("", "", "") == api.ReadDetailedVersionDirect(0)

        api._conforms_to_rp1210c = True
        assert True == api._conforms_to_rp1210c

        assert ("", "", "") == api.ReadDetailedVersionDirect(0)

    def test_RP1210API_GetErrorMsg(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert 'NO_ERRORS' == api.GetErrorMsg(0)

        def dummy(a, b):
            return 0

        api.dll.RP1210_GetErrorMsg = dummy

        assert '' == api.GetErrorMsg(0)

    def test_RP1210API_GetHardwareStatus(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert 129 == api.GetHardwareStatus(0, b'\x20')

        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert 129 == api.GetHardwareStatus(0, b'\x20', 1)

        api = RP1210.RP1210API(api_name='DLAUSB32')
        api.loadDLL()

        assert 129 == api.GetHardwareStatus(0, b'\x10')

    def test_RP1210API_GetHardwareStatusDirect(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' == api.GetHardwareStatusDirect(0)

    def test_RP1210API_SendCommand(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert 129 == api.SendCommand(0, 0)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        api.loadDLL()

        assert 129 == api.SendCommand(0, 0, b'\xff')

    def test_RP1210API__init_functions(self):
        api = RP1210.RP1210API(api_name='PEAKRP32')

        assert not api.dll

        api.loadDLL()

        assert api.dll
        assert True == api._conforms_to_rp1210c

        api._init_functions()

        assert [c_long, c_short, c_char_p, c_long, c_long, c_short] == api.dll.RP1210_ClientConnect.argtypes
        assert [c_short] == api.dll.RP1210_ClientDisconnect.argtypes
        assert [c_short, c_char_p, c_short, c_short, c_short] == api.dll.RP1210_SendMessage.argtypes
        assert [c_short, c_char_p, c_short, c_short] == api.dll.RP1210_ReadMessage.argtypes
        assert [c_char_p, c_char_p, c_char_p, c_char_p] == api.dll.RP1210_ReadVersion.argtypes
        assert [c_short, c_char_p] == api.dll.RP1210_GetErrorMsg.argtypes
        assert [c_short, c_char_p, c_short, c_short] == api.dll.RP1210_GetHardwareStatus.argtypes
        assert [c_short, c_short, c_char_p, c_short] == api.dll.RP1210_SendCommand.argtypes

        assert [c_short, c_char_p, c_char_p, c_char_p] == api.dll.RP1210_ReadDetailedVersion.argtypes
        assert [c_short, POINTER(c_int32), c_char_p, c_short] == api.dll.RP1210_GetLastErrorMsg.argtypes
        assert [c_short, c_long, c_void_p, c_void_p] == api.dll.RP1210_Ioctl.argtypes

        # cause the init function to enter except block
        api.dll.RP1210_ReadDetailedVersion = 0

        api._init_functions()
        assert False == api._conforms_to_rp1210c

    def test_RP1210API__get_alternate_dll_path(self):
        api = RP1210.RP1210API(api_name='')
        assert os.path.abspath('C:/Windows/.dll') == api._get_alternate_dll_path()
        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert os.path.abspath('C:/Windows/PEAKRP32.dll') == api._get_alternate_dll_path()

    def test_RP1210API__validate_and_fix_clientid(self):
        api = RP1210.RP1210API(api_name='')
        assert 0 == api._validate_and_fix_clientid(0)
        assert 1 == api._validate_and_fix_clientid(-1)
        assert 1 == api._validate_and_fix_clientid(1)
        assert 1 == api._validate_and_fix_clientid(0xF0001)
        assert 0 == api._validate_and_fix_clientid(0xFFFFF)
        assert 32768 == api._validate_and_fix_clientid(0x8000)
        assert 32766 == api._validate_and_fix_clientid(0x8001)

        api = RP1210.RP1210API(api_name='PEAKRP32')
        assert 0 == api._validate_and_fix_clientid(0)
        assert 63 == api._validate_and_fix_clientid(63)
        assert 64 == api._validate_and_fix_clientid(64)
        assert 129 == api._validate_and_fix_clientid(65)
        assert 129 == api._validate_and_fix_clientid(100)
        assert 129 == api._validate_and_fix_clientid(1000)

class Test_RP1210VendorList:
    def test_RP1210VendorList_init(self):
        vendorList = RP1210.RP1210VendorList()
        assert vendorList.vendors
        assert 0 == vendorList.vendorIndex
        assert 0 == vendorList.deviceIndex
        assert None == vendorList._rp121032_path
        assert None == vendorList._api_path
        assert None == vendorList._config_path

        vendorList = RP1210.RP1210VendorList(None, 'foo', 'bar')
        assert vendorList.vendors
        assert 0 == vendorList.vendorIndex
        assert 0 == vendorList.deviceIndex
        assert None == vendorList._rp121032_path
        assert 'foo' == vendorList._api_path
        assert 'bar' == vendorList._config_path

    def test_RP1210VendorList_get_vendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert 'PEAKRP32 - PEAK-System PCAN Adapter' == vendorList.vendor
        
        vendorList.vendorIndex = 1
        assert 'DLAUSB32 - Noregon Systems Inc., DLA+ 2.0 Adapter' == vendorList.vendor

    def test_RP1210VendorList_set_vendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 0 == vendorList.vendorIndex

        vendorList.vendor = 'DLAUSB32'

        assert 1 == vendorList.vendorIndex

        vendorList.vendor = 'PEAKRP32'

        assert 0 == vendorList.vendorIndex

    def test_RP1210VendorList_get_api(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert RP1210.RP1210API('PEAKRP32') == vendorList.api

        vendorList.vendor = 'DLAUSB32'
        assert RP1210.RP1210API('DLAUSB32') == vendorList.api

    def test_RP1210VendorList_get_set_device(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert '1 - PEAK-System CAN Adapter (USB, 1 Channel)' == str(vendorList.device)

        vendorList.vendor = 'NULN2R32'
        assert '1 - USB-Link 2' == str(vendorList.device)

        vendorList.device = 2
        assert '2 - Bluetooth USB-Link 2' == str(vendorList.device)

    def test_RP1210VendorList_get_item(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert RP1210.RP1210Config('PEAKRP32') == vendorList.__getitem__(0)
        assert RP1210.RP1210Config('DLAUSB32') == vendorList.__getitem__(1)

    def test_RP1210VendorList_bool(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert True == bool(vendorList)
        vendorList.vendors = []
        assert False == bool(vendorList)

    def test_RP1210VendorList_len(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert 8 == len(vendorList)
        vendorList.vendors = []
        assert 0 == len(vendorList)

    def test_RP1210VendorList_str(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert 'PEAKRP32 - PEAK-System PCAN Adapter, DLAUSB32 - Noregon Systems Inc., DLA+ 2.0 Adapter, DGDPA5MA - DG Technologies DPA 5 Multi Application, CIL7R32 - Cummins Inc. INLINE7, NULN2R32 - NEXIQ Technologies USB-Link 2, CMNSI632 - Cummins Inc. INLINE6, DrewLinQ - DrewLinQ - Drew Technologies, Inc., DTKRP32 - Drew Technologies Inc.' == str(vendorList)
        vendorList.vendors = []
        assert '' == str(vendorList)

    def test_RP1210VendorList_populate(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        vendorList.vendors = []
        assert not vendorList.vendors
        vendorList.populate()
        assert vendorList.vendors
        assert 'PEAKRP32 - PEAK-System PCAN Adapter, DLAUSB32 - Noregon Systems Inc., DLA+ 2.0 Adapter, DGDPA5MA - DG Technologies DPA 5 Multi Application, CIL7R32 - Cummins Inc. INLINE7, NULN2R32 - NEXIQ Technologies USB-Link 2, CMNSI632 - Cummins Inc. INLINE6, DrewLinQ - DrewLinQ - Drew Technologies, Inc., DTKRP32 - Drew Technologies Inc.' == str(vendorList)

    def test_RP1210VendorList_addVendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        vendorList.vendors = []
        assert not vendorList.vendors
        assert 0 == len(vendorList)

        vendorList.addVendor('PEAKRP32')
        assert 1 == len(vendorList)

        vendorList.addVendor(RP1210.RP1210Config('PEAKRP32'))
        assert 2 == len(vendorList)

        with pytest.raises(TypeError):
            vendorList.addVendor(0)
        assert 2 == len(vendorList)

    def test_RP1210VendorList_getList(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
       
        vlist = vendorList.getList()
        assert len(vlist) == 8 
        for v in vlist:
            assert isinstance(v, RP1210.RP1210Config)

    def test_RP1210VendorList_getVendorList(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
       
        vlist = vendorList.getVendorList()
        assert len(vlist) == 8 
        for v in vlist:
            assert isinstance(v, RP1210.RP1210Config)

    def test_RP1210VendorList_getAPI(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
       
        assert RP1210.RP1210API('PEAKRP32') == vendorList.getAPI()
        vendorList.vendor = 'DLAUSB32'
        assert RP1210.RP1210API('DLAUSB32') == vendorList.getAPI()

        vendorList.vendorIndex = 'f'
        assert None == vendorList.getAPI()

    def test_RP1210VendorList_numVendors(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
       
        assert 8 == vendorList.numVendors()
        vendorList.vendors = []
        assert 0 == vendorList.numVendors()
        vendorList.vendors = 10
        assert 0 == vendorList.numVendors()

    def test_RP1210VendorList_numDevices(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        
        vendorList.vendor = 'NULN2R32'
        assert 3 == vendorList.numDevices()
        vendorList.vendor = 'PEAKRP32'
        assert 1 == vendorList.numDevices()

    @patch.object(RP1210.RP1210Config, 'getDevices')
    def test_RP1210VendorList_numDevices_exception(self, patch_fn):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        
        patch_fn.return_value = 0
        assert 0 == vendorList.numDevices()

    def test_RP1210VendorList_setVendorIndex(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 0 == vendorList.vendorIndex
        assert 0 == vendorList.deviceIndex

        vendorList.deviceIndex = 9
        assert 9 == vendorList.deviceIndex

        vendorList.setVendorIndex(20)

        assert 20 == vendorList.vendorIndex
        assert 0 == vendorList.deviceIndex

    def test_RP1210VendorList_setVendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert RP1210.RP1210Config('PEAKRP32')  == vendorList.vendor

        vendorList.vendor = 'DLAUSB32'
        assert RP1210.RP1210Config('DLAUSB32')  == vendorList.vendor

        vendorList.vendor = RP1210.RP1210Config('NULN2R32')
        assert RP1210.RP1210Config('NULN2R32')  == vendorList.vendor


        vendorList.vendor = RP1210.RP1210Config('foo')
        assert RP1210.RP1210Config('foo')  == vendorList.vendor

        with pytest.raises(TypeError):
            vendorList.vendor = 0
        assert RP1210.RP1210Config('foo')  == vendorList.vendor # not changed

    def test_RP1210VendorList_setDeviceIndex(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 0 == vendorList.deviceIndex
        vendorList.setDeviceIndex(1)
        assert 1 == vendorList.deviceIndex
        vendorList.setDeviceIndex(0)
        assert 0 == vendorList.deviceIndex

    def test_RP1210VendorList_setDevice(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        vendorList.vendor = 'NULN2R32'

        assert 1 == vendorList.device.getID()

        vendorList.setDevice(2)

        assert 2 == vendorList.device.getID()

        vendorList.setDevice(1)

        assert 1 == vendorList.device.getID()

        with pytest.raises(TypeError):
            vendorList.setDevice('f')

    def test_RP1210VendorList_getDeviceIndex(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        vendorList.vendor = 'NULN2R32'

        assert 0 == vendorList.getDeviceIndex()
        assert 1 == vendorList.getDeviceIndex(2) # 1 indexed
        device = vendorList.getCurrentDevice()
        assert 0 == vendorList.getDeviceIndex(device)
        assert 0 == vendorList.getDeviceIndex(9)

    @patch.object(RP1210.RP1210Config, 'getDevices')
    def test_RP1210VendorList_getDeviceIndex_exception(self, patch_fn):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        patch_fn.return_value = 0
        assert 0 == vendorList.getDeviceIndex(0)

    def test_RP1210VendorList_getVendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert RP1210.RP1210Config('PEAKRP32') == vendorList.getVendor()
        assert RP1210.RP1210Config('NULN2R32') == vendorList.getVendor('NULN2R32')
        assert RP1210.RP1210Config('PEAKRP32') == vendorList.getVendor(0)
        assert None == vendorList.getVendor({})

    def test_RP1210VendorList_getVendorIndex(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 0 == vendorList.getVendorIndex()
        assert 0 == vendorList.getVendorIndex('PEAKRP32')
        assert 4 == vendorList.getVendorIndex('NULN2R32')
        assert 0 == vendorList.getVendorIndex('foo')
        vendorList.vendors = 0
        assert 0 == vendorList.getVendorIndex('foo')

    def test_RP1210VendorList_getCurrentVendor(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert RP1210.RP1210Config('PEAKRP32') == vendorList.getCurrentVendor()
        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 
        assert RP1210.RP1210Config('NULN2R32') == vendorList.getCurrentVendor()
        vendorList.vendor = RP1210.RP1210Config('PEAKRP32') 
        assert RP1210.RP1210Config('PEAKRP32') == vendorList.getCurrentVendor()

        vendorList.vendorIndex = {}
        assert None == vendorList.getCurrentVendor()

    def test_RP1210VendorList_getVendorName(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 'PEAK-System PCAN Adapter' == vendorList.getVendorName()
        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 
        assert 'NEXIQ Technologies USB-Link 2' == vendorList.getVendorName()
        vendorList.vendor = RP1210.RP1210Config('PEAKRP32') 
        assert 'PEAK-System PCAN Adapter' == vendorList.getVendorName()

        vendorList.vendorIndex = {}
        assert "" == vendorList.getVendorName()
   
    def test_RP1210VendorList_getCurrentDevice(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 

        assert '1 - USB-Link 2' == str(vendorList.getCurrentDevice())
        vendorList.setDeviceIndex(1)
        assert '2 - Bluetooth USB-Link 2' == str(vendorList.getCurrentDevice())

        vendorList.deviceIndex = 69420
        assert '1 - USB-Link 2' == str(vendorList.getCurrentDevice())
        assert 0 == vendorList.deviceIndex

        vendorList.deviceIndex = 69420
        def dummy():
            return []
        vendorList.vendor.getDevices = dummy
        assert None == vendorList.getCurrentDevice()

        vendorList.deviceIndex = 69420
        def dummy():
            return 0
        vendorList.vendor.getDevices = dummy
        assert None == vendorList.getCurrentDevice()

    def test_RP1210VendorList_getDeviceID(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 

        assert 1 == vendorList.getDeviceID()
       
        vendorList.getCurrentDevice = 0
        assert -1 == vendorList.getDeviceID()

    def test_RP1210VendorList_getVendorNames(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert ['PEAK-System PCAN Adapter', 'Noregon Systems Inc., DLA+ 2.0 Adapter', 'DG Technologies DPA 5 Multi Application', 'Cummins Inc. INLINE7', 'NEXIQ Technologies USB-Link 2', 'Cummins Inc. INLINE6', 'DrewLinQ - Drew Technologies, Inc.', 'Drew Technologies Inc.'] == vendorList.getVendorNames()

    def test_RP1210VendorList_getAPIName(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 'PEAKRP32' == vendorList.getAPIName()
        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 
        assert 'NULN2R32' == vendorList.getAPIName()
        vendorList.vendor = RP1210.RP1210Config('PEAKRP32') 
        assert 'PEAKRP32' == vendorList.getAPIName()

    def test_RP1210VendorList_getAPINames(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert ['PEAKRP32', 'DLAUSB32', 'DGDPA5MA', 'CIL7R32', 'NULN2R32', 'CMNSI632', 'DrewLinQ', 'DTKRP32'] == vendorList.getAPINames()

    def test_RP1210VendorList_getDeviceIDs(self):
        vendorList = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        vendorList.vendor = RP1210.RP1210Config('NULN2R32') 
        assert [1, 2, 3] == vendorList.getDeviceIDs()

class Test_RP1210Client:
    def test_RP1210Client_init(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 128 == client.clientID

    def test_RP1210Client_str(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 'PEAK-System PCAN Adapter' == str(client)

        client.vendor = 'NULN2R32' 

        assert 'NEXIQ Technologies USB-Link 2' == str(client)

        client.vendor = 'PEAKRP32' 

        assert 'PEAK-System PCAN Adapter' == str(client)

    def test_RP1210Client_int(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 128 == int(client)

        client.clientID = 69420

        assert 69420 == int(client)

    def test_RP1210Client_getClientID(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        assert 128 == client.getClientID()

        client.clientID = 69420

        assert 69420 == client.getClientID()

    def test_RP1210Client_connect(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert 129 == client.connect()

        client.vendor._api_valid = False
        assert False == client.vendor._api_valid

        assert 128 == client.connect()

        def dummy():
            return 0

        client.getCurrentVendor = dummy

        assert 128 == client.connect()

    def test_RP1210Client_disconnect(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
        assert 129 == client.disconnect()

        def dummy():
            return 0

        client.getAPI = dummy

        assert 128 == client.disconnect()

    def test_RP1210Client_command(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.command(0)

        def dummy():
            return 0

        client.getAPI = dummy

        assert -1 == client.command(0)

    def test_RP1210Client_rx(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert b'' == client.rx()

    def test_RP1210Client_tx(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.tx(b'')
        assert 128 == client.tx(0)

    def test_RP1210Client_resetDevice(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.resetDevice()

    def test_RP1210Client_setAllFiltersToPass(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setAllFiltersToPass()

    def test_RP1210Client_setJ1939Filters(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setJ1939Filters(0)

    def test_RP1210Client_setCANFilters(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setCANFilters(0, 0, 0)

    def test_RP1210Client_setEcho(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setEcho()

    def test_RP1210Client_setAllFiltersToDiscard(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setAllFiltersToDiscard()

    def test_RP1210Client_setMessageReceive(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setMessageReceive()

    def test_RP1210Client_protectJ1939Address(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.protectJ1939Address(0, 0)

    def test_RP1210Client_releaseJ1939Address(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.releaseJ1939Address(0)

    def test_RP1210Client_setJ1939FilterType(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setJ1939FilterType(0)

    def test_RP1210Client_setCANFilterType(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setCANFilterType(0)

    def test_RP1210Client_setJ1939InterpacketTime(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setJ1939InterpacketTime(0)

    def test_RP1210Client_setMaxErrorMsgSize(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setMaxErrorMsgSize(0)

    def test_RP1210Client_disallowConnections(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.disallowConnections()

    def test_RP1210Client_setJ1939Baud(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setJ1939Baud(0)

    def test_RP1210Client_setBlockingTimeout(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setBlockingTimeout(0, 0)

    def test_RP1210Client_flushBuffers(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.flushBuffers()

    def test_RP1210Client_getBaud(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert "b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'" == client.getBaud()

    def test_RP1210Client_setCANBaud(self):
        client = RP1210.RP1210Client(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)

        client.clientID = 0

        assert 129 == client.setCANBaud(0)
