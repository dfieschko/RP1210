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
    assert RP1210.translateErrorCode(-128) == "ERR_DLL_NOT_INITIALIZED"

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
    assert rp1210.CANAutoBaud() == False
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

def test_InvalidAPIName_Devices_Protocols():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.getDevices() == []
    assert rp1210.getProtocols() == []
    assert rp1210.getProtocol(3) == None
    assert rp1210.getDevice(3) == None

def test_InvalidAPIName_load_dll():
    api_name = "CHUNGLEBUNGUS"
    assert api_name not in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.api.getDLL() == None



def test_RP1210Interface_DearbornDPA5Pro():
    """
    Tests the RP1210Interface class with Dearborn DPA5 Pro drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "DGDPA5MA"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.isValid() == True
    assert str(rp1210) == api_name + " - DG Technologies DPA 5 Multi Application"
    assert rp1210.getAPIName() == api_name
    assert rp1210.getName() == "DG Technologies DPA 5 Multi Application"
    assert rp1210.getAddress1() == "DG Technologies"
    assert rp1210.getAddress2() == "33604 West 8 Mile Road"
    assert rp1210.getCity() == "Farmington Hills"
    assert rp1210.getState() == "MI"
    assert rp1210.getCountry() == "USA"
    assert rp1210.getPostal() == "48335"
    assert rp1210.getTelephone() == "248-888-2000"
    assert rp1210.getFax() == "248-888-9977"
    assert rp1210.getVendorURL() == "http://www.dgtech.com"
    assert rp1210.getVersion() == "4.04"
    assert rp1210.autoDetectCapable() == True
    assert rp1210.getTimeStampWeight() == 1000
    assert rp1210.getMessageString() == "dgDPA5MessageString"
    assert rp1210.getErrorString() == "dgDPA5ErrorString"
    assert rp1210.getRP1210Version() == "C"
    assert rp1210.getDebugLevel() == 0
    assert rp1210.getDebugFile() == "C:\\DGTech\\DPA 5\\Utilities\\DGDPA5MA_Log.txt"
    assert rp1210.getDebugMode() == 1
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.CANAutoBaud() == True
    assert rp1210.getCANFormatsSupported() == [4, 5]
    assert rp1210.getJ1939FormatsSupported() == [1, 2]
    assert rp1210.getDevices() == [1, 2]
    assert rp1210.getProtocols() == [100,101,102,103,104,105,106,107,108,109,110,111]

def test_RP1210Interface_NoregonDLA2():
    """
    Tests the RP1210Interface class with Noregon DLA 2.0 drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "DLAUSB32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.isValid() == True
    assert str(rp1210) == api_name + " - Noregon Systems Inc., DLA+ 2.0 Adapter"
    assert rp1210.getAPIName() == api_name
    assert rp1210.getName() == "Noregon Systems Inc., DLA+ 2.0 Adapter"
    assert rp1210.getAddress1() == "7009 Albert Pick Rd."
    assert rp1210.getAddress2() == ""
    assert rp1210.getCity() == "Greensboro"
    assert rp1210.getState() == "NC"
    assert rp1210.getCountry() == "USA"
    assert rp1210.getPostal() == "27409"
    assert rp1210.getTelephone() == "+1 (336) 970-5567"
    assert rp1210.getFax() == ""
    assert rp1210.getVendorURL() == "www.JPROFleetProducts.com"
    assert rp1210.getVersion() == "4"
    assert rp1210.autoDetectCapable() == True
    assert rp1210.CANAutoBaud() == True
    assert rp1210.getTimeStampWeight() == 1000
    assert rp1210.getMessageString() == "NSICAN_READ_NOTIFY"
    assert rp1210.getErrorString() == "NSICAN_SEND_NOTIFY"
    assert rp1210.getRP1210Version() == "C"
    assert rp1210.getDebugLevel() == 0
    assert rp1210.getDebugFile() == "C:\\Noregon\\dlausb32\\dlausb32.log"
    assert rp1210.getDebugMode() == 1
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == [4,5]
    assert rp1210.getJ1939FormatsSupported() == [1,2]
    assert rp1210.getDevices() == [100]
    assert rp1210.getProtocols() == [51,52,53,54,55,56,58,59,60,61,62,63]

def test_RP1210Interface_NoregonDLA2_Devices():
    """
    Tests the Device class with Noregon DLA 2.0 drivers.

    You must have these drivers installed to run this test.
    """
    api_name = "DLAUSB32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    deviceIDs = rp1210.getDevices()
    assert deviceIDs == [100]
    device100 = rp1210.getDevice(100)
    assert device100.getID() == 100
    assert device100.getDescription() == "DLA+ 2.0, USB"
    assert device100.getName() == "DLA+ 2.0"
    assert device100.getParams() == "USB:CAN1:250"

def test_RP1210Interface_NEMESIS():
    """
    Tests the RP1210Interface class with Cummins' NEMESIS dummy drivers, which are invalid.

    You must have these drivers installed to run this test.
    """
    api_name = "CMNSIM32"
    assert api_name in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(api_name)
    assert rp1210.isValid() == False
    assert str(rp1210) == api_name + " - Cummins Inc. NEMESIS Mock RP1210 Driver - (drivers invalid)"

