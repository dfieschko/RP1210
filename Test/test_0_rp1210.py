from configparser import ConfigParser
import os
from RP1210 import sanitize_msg_param
import RP1210
from RP1210.RP1210 import getAPINames

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

def test_getAPINames():
    """
    The following drivers must be installed for this test:
    
    - Noregon DLA 2.0
    - Nexiq USB-Link 2
    """
    assert RP1210.getAPINames() != None
    api_names = RP1210.getAPINames()
    assert "DLAUSB32" in api_names
    assert "NULN2R32" in api_names
    

def test_getAPINames_notfound():
    """test getAPINames when file doesn't exist at path"""
    path = "doesnt_exist.ini"
    result = RP1210.getAPINames(path)
    assert result == []

def test_getAPINames_empty():
    """generate empty file and provide its path to getAPINames"""
    # generate file
    path = "getAPINames_empty.ini"
    create_file(path)
    # test output
    result = RP1210.getAPINames(path)
    assert result == []

def test_getAPINames_invalid():
    """generate an invalid file and provide its path to getAPINames"""
    # generate file
    path = "getAPINames_invalid.ini"
    parser = create_file(path)
    parser.add_section("[")
    with open(path, 'w') as file:
        parser.write(file)
    # test output
    assert RP1210.getAPINames(path) == []

def test_delete_files():
    """Deletes the files created by other tests."""
    delete_file("getAPINames_empty.ini")
    delete_file("getAPINames_invalid.ini")

def test_clientid_translation():
    assert RP1210.translateErrorCode(0) == "NO_ERRORS"
    assert RP1210.translateErrorCode(1) == "NO_ERRORS"
    assert RP1210.translateErrorCode(25) == "NO_ERRORS"
    assert RP1210.translateErrorCode(127) == "NO_ERRORS"
    assert RP1210.translateErrorCode(128) == "ERR_DLL_NOT_INITIALIZED"
    assert RP1210.translateErrorCode(151) == "ERR_BUS_OFF"
    assert RP1210.translateErrorCode(159) == "ERR_MESSAGE_NOT_SENT"
    assert RP1210.translateErrorCode(165) == "165"
    assert RP1210.translateErrorCode(207) == "ERR_DEVICE_NOT_SUPPORTED"
    assert RP1210.translateErrorCode(454) == "ERR_CAN_BAUD_SET_NONSTANDARD"
    assert RP1210.translateErrorCode(601) == "ERR_NULL_PARAMETER"
    assert RP1210.translateErrorCode(623423401) == "623423401"
    assert RP1210.translateErrorCode(-128) == "ERR_DLL_NOT_INITIALIZED"

def test_RP1210Interface_InvalidAPIName():
    """
    Tests the RP1210Interface class with an API name that doesn't exist.
    """
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - (Vendor Name Missing) - (drivers invalid)"
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
    assert rp1210.getTimeStampWeight() == None
    assert rp1210.getMessageString() == ""
    assert rp1210.getErrorString() == ""
    assert rp1210.getRP1210Version() == ""
    assert rp1210.getDebugLevel() == -1
    assert rp1210.getDebugFile() == ""
    assert rp1210.getDebugMode() == None
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == []
    assert rp1210.getJ1939FormatsSupported() == []
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolNames() == []
    assert rp1210.getProtocolIDs() == []
    assert rp1210.isValid() == False

def test_InvalidAPIName_Devices_Protocols():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.getDeviceIDs() == []
    assert rp1210.getProtocolIDs() == []
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

def test_RP1210Interface_NEMESIS():
    """
    Tests the RP1210Interface class with Cummins' NEMESIS dummy drivers, which are invalid.

    You must have these drivers installed to run this test.
    """
    api_name = "CMNSIM32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - Cummins Inc. NEMESIS Mock RP1210 Driver - (drivers invalid)"
    devices = rp1210.getDeviceIDs()
    device = rp1210.getDevice(devices[0])
    assert str(device) == str(device.getID()) + " - " + device.getDescription()

def test_sanitize_msg_param_bytes():
    assert sanitize_msg_param(b'0') == b'0'
    assert sanitize_msg_param(b'\x00') == b'\x00'
    assert sanitize_msg_param(b'16') == b'16'
    assert sanitize_msg_param(b'\x10') == b'\x10'
    assert sanitize_msg_param(b'0', 2) == b'\x000'
    assert sanitize_msg_param(b'\x00', 2) == b'\x00\x00'
    assert sanitize_msg_param(b'') == b''
    assert sanitize_msg_param(b'', 4) == b'\x00\x00\x00\x00'
    
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

def test_vendorlist_init():
    """
    Initializes VendorList just to see if the program crashes, but doesn't do much else.
    Doesn't require any adapter software to be installed.
    """
    vendors = RP1210.RP1210VendorList()

def test_vendorlist_rp1210config_objects():
    """
    Makes sure that all RP1210Config objects that are possible to read from
    RP121032.ini are present in RP1210VendorList.
    """
    vendor_names = getAPINames()
    assert vendor_names
    vendors = RP1210.RP1210VendorList()
    assert vendors
    for vendor in vendors.getList():
        assert vendor.getAPIName() in vendor_names

def test_vendorlist_index():
    """
    Iterates through a bunch of indices for vendors and devices to make sure an invalid index
    doesn't cause a crash.
    """
    vendors = RP1210.RP1210VendorList()
    for x in range(-10, 50):
        vendors.setVendorIndex(x)
        vendors.getVendor(x)
        vendors.getCurrentVendor()
        for y in range(-10, 1000):
            vendors.setDeviceIndex(y)
            vendors.getCurrentDevice()
        vendors.getAPI()

def test_rp1210client_populate_logic():
    """Tests whether RP1210Client recognizes relevant drivers when adapter is disconnected."""
    vendors = []
    vendors.clear()
    api_list = RP1210.getAPINames()
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
