from configparser import ConfigParser
import os
from RP1210C import RP1210

def delete_file(path : str):
    if os.path.exists(path):
        os.remove(path)

def create_file(path : str) -> ConfigParser:
    """creates an empty file."""
    parser = ConfigParser()
    file = open(path, 'w')
    parser.clear()
    parser.write(file)
    return parser

def test_getAPINames_only():
    """Just check to make sure it doesn't crash"""
    RP1210.getAPINames()

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
    file = open(path, 'w')
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
    assert RP1210.translateErrorCode(-234235) == "-234235"

def test_RP1210Interface_InvalidAPIName():
    """
    Tests the RP1210Interface class with an API name that doesn't exist.
    """
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
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
    assert rp1210.getVersion() == None
    assert rp1210.autoDetectCapable() == False
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
    assert rp1210.getDevices() == []
    assert rp1210.getProtocols() == []

def test_RP1210Interface_ACTIA():
    """
    Tests the RP1210Interface class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "IMBRP32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.isValid() == True
    assert str(rp1210) == api_name + " - I+ME ACTIA GmbH"
    assert rp1210.getAPIName() == api_name
    assert rp1210.getName() == "I+ME ACTIA GmbH"
    assert rp1210.getAddress1() == ""
    assert rp1210.getAddress2() == ""
    assert rp1210.getCity() == ""
    assert rp1210.getState() == ""
    assert rp1210.getCountry() == ""
    assert rp1210.getPostal() == ""
    assert rp1210.getTelephone() == ""
    assert rp1210.getFax() == ""
    assert rp1210.getVendorURL() == ""
    assert rp1210.getVersion() == None
    assert rp1210.autoDetectCapable() == False
    assert rp1210.getTimeStampWeight() == 100
    assert rp1210.getMessageString() == "IME RP1210 Interrupt BasicXS"
    assert rp1210.getErrorString() == "IME RP1210 Error BasicXS"
    assert rp1210.getRP1210Version() == ""
    assert rp1210.getDebugLevel() == -1
    assert rp1210.getDebugFile() == ""
    assert rp1210.getDebugMode() == None
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == []
    assert rp1210.getJ1939FormatsSupported() == []
    assert rp1210.getDevices() == [1, 2, 3]
    assert rp1210.getProtocols() == [1, 2, 3]

def test_RP1210Interface_ACTIA_Devices():
    """
    Tests the Device class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "IMBRP32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    deviceIDs = rp1210.getDevices()
    assert deviceIDs == [1, 2, 3]
    device1 = rp1210.getDevice(1)
    assert device1.getID() == 1
    assert device1.getDescription() == "BasicXS, USB"
    assert device1.getName() == "BasicXS USB"
    assert device1.getParams() == ""
    device2 = rp1210.getDevice(2)
    assert device2.getID() == 2
    assert device2.getDescription() == "BasicXS, COM1"
    assert device2.getName() == "BasicXS COM1"
    assert device2.getParams() == ""
    device3 = rp1210.getDevice(3)
    assert device3.getID() == 3
    assert device3.getDescription() == "BasicXS, COM2"
    assert device3.getName() == "BasicXS COM2"
    assert device3.getParams() == ""

def test_RP1210Interface_ACTIA_Protocols():
    """
    Tests the Device class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "IMBRP32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    protocolIDs = rp1210.getProtocols()
    assert protocolIDs == [1, 2, 3]
    protocol1 = rp1210.getProtocol(1)
    assert protocol1.getDescription() == "Generic CAN"
    assert protocol1.getString() == "CAN"
    assert protocol1.getParams() == ""
    assert protocol1.getDevices() == [1, 2, 3]
    protocol2 = rp1210.getProtocol(2)
    assert protocol2.getDescription() == "J1708 Link Layer Protocol"
    assert protocol2.getString() == "J1708"
    assert protocol2.getParams() == ""
    assert protocol2.getDevices() == [1, 2, 3]
    protocol3 = rp1210.getProtocol(3)
    assert protocol3.getDescription() == "J1939 Link Layer Protocol"
    assert protocol3.getString() == "J1939"
    assert protocol3.getParams() == ""
    assert protocol3.getDevices() == [1, 2, 3]

def test_RP1210Interface_DearbornDPA5Pro():
    """
    Tests the RP1210Interface class with Dearborn DPA5 Pro drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "DGDPA5MA"
    assert api_name in RP1210.getAPINames()
    

def test_RP1210Interface_Nexiq():
    """
    Tests the RP1210Interface class with Nexiq USB-Link 3 drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "NULN2R32"
    assert api_name in RP1210.getAPINames()

def test_RP1210Interface_NoregonDLA2():
    """
    Tests the RP1210Interface class with Noregon DLA 2.0 drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "DLAUSB32"
    assert api_name in RP1210.getAPINames()

def test_RP1210Interface_NEMESIS():
    """
    Tests the RP1210Interface class with Cummins' NEMESIS dummy drivers, which are invalid.

    You must have these drivers installed to run this test.
    """
    api_name = "CMNSIM32"
