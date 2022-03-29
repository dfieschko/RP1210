import pytest
import RP1210, os, configparser
from utilities import RP1210ConfigTestUtility

API_NAMES = ["PEAKRP32", "DLAUSB32", "NULN2R32", "CMNSI632", "DGDPA5MA"]

# These tests are meant to be run with cwd @ repository's highest-level directory
CWD = os.getcwd()
TEST_FILES_DIRECTORY = CWD + ".\\Test\\test-files"
INI_DIRECTORY = TEST_FILES_DIRECTORY + "\\ini-files"
DLL_DIRECTORY = TEST_FILES_DIRECTORY + "\\dlls"
RP121032_PATH = TEST_FILES_DIRECTORY + "\\RP121032.ini"

def test_cwd():
    """Make sure cwd isn't in Test folder."""
    cwd = os.getcwd()
    assert "RP1210" in cwd
    assert "Test" not in cwd

def test_getAPINames():
    """
    Test the getAPINames() function with a custom directory.
    
    Also calls getAPINames() with no argument to make sure there isn't an exception.
    """
    RP1210.getAPINames()
    assert RP1210.getAPINames(RP121032_PATH) == API_NAMES

@pytest.mark.parametrize("rp121032_path", ["bork", "bork.ini", 1234, "RP121032", RP121032_PATH + "x"])
def test_getAPINames_invalid(rp121032_path):
    """
    Makes sure we get an exception if we provide an invalid path for getAPINames().
    - xfail = success
    - xpass = fail
    """
    with pytest.raises(FileNotFoundError):
        RP1210.getAPINames(rp121032_path)


@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210Config(api_name : str):
    """
    Tests RP1210Config class with all sample files provided in test-files folder.
    """
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    assert api_name in RP1210.getAPINames(RP121032_PATH)
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    assert rp1210.isValid() == True     
    assert rp1210.getAPIName() == api_name
    assert utility.verifydata(rp1210.getName, "VendorInformation", "Name")
    assert utility.verifydata(rp1210.getAddress1, "VendorInformation", "Address1")
    assert utility.verifydata(rp1210.getAddress2, "VendorInformation", "Address2")
    assert utility.verifydata(rp1210.getCity, "VendorInformation", "City")
    assert utility.verifydata(rp1210.getState, "VendorInformation", "State")
    assert utility.verifydata(rp1210.getCountry, "VendorInformation", "Country")
    assert utility.verifydata(rp1210.getPostal, "VendorInformation", "Postal")
    assert utility.verifydata(rp1210.getTelephone, "VendorInformation", "Telephone")
    assert utility.verifydata(rp1210.getFax, "VendorInformation", "Fax")
    assert utility.verifydata(rp1210.getVendorURL, "VendorInformation", "VendorURL")
    assert utility.verifydata(rp1210.getVersion, "VendorInformation", "Version")
    assert utility.verifydata(rp1210.autoDetectCapable, "VendorInformation", "AutoDetectCapable")
    assert utility.verifydata(rp1210.getAutoDetectCapable, "VendorInformation", "AutoDetectCapable")
    assert utility.verifydata(rp1210.getTimeStampWeight, "VendorInformation", "TimeStampWeight")
    assert utility.verifydata(rp1210.getMessageString, "VendorInformation", "MessageString")
    assert utility.verifydata(rp1210.getErrorString, "VendorInformation", "ErrorString")
    assert utility.verifydata(rp1210.getRP1210Version, "VendorInformation", "RP1210")
    assert utility.verifydata(rp1210.getDebugLevel, "VendorInformation", "DebugLevel")
    assert utility.verifydata(rp1210.getDebugFile, "VendorInformation", "DebugFile")
    assert utility.verifydata(rp1210.getDebugMode, "VendorInformation", "DebugMode")
    assert utility.verifydata(rp1210.getDebugFileSize, "VendorInformation", "DebugFileSize")
    assert utility.verifydata(rp1210.getNumberOfSessions, "VendorInformation", "NumberOfRTSCTSSessions")
    assert utility.verifydata(rp1210.getCANAutoBaud, "VendorInformation", "CANAutoBaud")
    assert utility.verifydata(rp1210.getCANFormatsSupported, "VendorInformation", "CANFormatsSupported")
    assert utility.verifydata(rp1210.getJ1939FormatsSupported, "VendorInformation", "J1939FormatsSupported")
    assert utility.verifydata(rp1210.getDeviceIDs, "VendorInformation", "Devices")
    assert utility.verifydata(rp1210.getProtocolIDs, "VendorInformation", "Protocols")
    
@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_Devices(api_name : str):
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    deviceIDs = rp1210.getDeviceIDs()
    for id in deviceIDs:
        device = rp1210.getDevice(id)
        assert utility.verifydevicedata(device.getID, id, "DeviceID")
        assert utility.verifydevicedata(device.getDescription, id, "DeviceDescription")
        assert utility.verifydevicedata(device.getName, id, "DeviceName")
        assert utility.verifydevicedata(device.getParams, id, "DeviceParams")
        assert utility.verifydevicedata(device.getMultiJ1939Channels, id, "MultiJ1939Channels")
        assert utility.verifydevicedata(device.getMultiCANChannels, id, "MultiCANChannels")
        assert str(device) == str(device.getID()) + " - " + device.getDescription()

'''
def test_Protocols(apiname : str):
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    protocolIDs = rp1210.getProtocolIDs()
    assert protocolIDs == [100,101,102,103,104,105,106,107,108,109,110,111]
    assert rp1210.getProtocolNames() == ["J1939", "J1708", "CAN", "J1850_104K", "J1850_416K", "PLC", "ISO15765",
                                    "ISO14230", "ISO9141", "J2284", "IESCAN", "J1850"]
    assert rp1210.getProtocol("J1939").getString() == "J1939"
    protocol1 = rp1210.getProtocol(100)
    assert protocol1.getDescription() == "SAE J1939 Protocol"
    assert protocol1.getString() == "J1939"
    assert protocol1.getParams() == "FAST_TRANSPORT"
    assert protocol1.getDevices() == [1, 2]
    assert protocol1.getSpeed() == ["125","250","500","666","1000","Auto"]
    protocol2 = rp1210.getProtocol(102)
    assert protocol2.getDescription() == "CAN Network Protocol"
    assert protocol2.getString() == "CAN"
    assert protocol2.getParams() == ""
    assert protocol2.getDevices() == [1, 2]
    assert protocol2.getSpeed() == ["125","250","500","666","1000","Auto"]

def test_load_DLL(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.getDLL() != None
    rp12102 = RP1210.RP1210Config(API_NAME)
    assert rp12102.api.loadDLL() != None

def test_disconnected_ClientConnect(apiname : str):
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    clientID = rp1210.api.ClientConnect(1, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in [ "ERR_OPENING_PORT", 
                                                    "ERR_HARDWARE_NOT_RESPONDING",
                                                    "ERR_INVALID_PROTOCOL"]

def test_disconnected_ClientDisconnect(apiname : str):
    """Tests whether ClientDisconnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    code = rp1210.api.ClientDisconnect(0)
    assert code >= 128

def test_disconnected_ReadVersion(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    buff1 = create_string_buffer(16)
    buff2 = create_string_buffer(16)
    buff3 = create_string_buffer(16)
    buff4 = create_string_buffer(16)
    rp1210.api.ReadVersion(buff1, buff2, buff3, buff4)
    assert buff1.value == b"0"
    assert buff2.value == b"0"
    assert buff3.value == b"3"
    assert buff4.value == b"0"

def test_disconnected_ReadVersionDirect(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.ReadVersionDirect() == ("0.0", "3.0")

def test_disconnected_ReadDetailedVersion(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    buff1 = create_string_buffer(17)
    buff2 = create_string_buffer(17)
    buff3 = create_string_buffer(17)
    ret_val = rp1210.api.ReadDetailedVersion(0, buff1, buff2, buff3)
    assert RP1210.translateErrorCode(ret_val) in ["ERR_DLL_NOT_INITIALIZED", "ERR_HARDWARE_NOT_RESPONDING", "ERR_INVALID_CLIENT_ID"]

def test_disconnected_GetErrorMsg(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    for code in RP1210.RP1210_ERRORS:
        msg = rp1210.api.GetErrorMsg(code)
        # Dearborn DPA5 has nonstandard error codes - don't check against dict for correctness

def test_disconnected_SendCommand(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    for command in RP1210.RP1210_COMMANDS:
        assert rp1210.api.SendCommand(command, 0) in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatus(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    buffer = create_string_buffer(64)
    ret_val = rp1210.api.GetHardwareStatus(0, buffer, 64)
    assert not buffer.value
    assert ret_val in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatusDirect(apiname : str):
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert not rp1210.api.GetHardwareStatusDirect(0).value

def test_disconnected_RemainingFunctions(apiname : str):
    """Tests whether API functions follow expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    ret_val = rp1210.api.SendMessage(0, b"", 0)
    assert ret_val >= 128
    assert ret_val in RP1210.RP1210_ERRORS
    ret_val = rp1210.api.SendMessage(0, b"12345678", 8)
    assert ret_val >= 128
    assert ret_val in RP1210.RP1210_ERRORS
    read_array_in = create_string_buffer(256)
    assert rp1210.api.ReadMessage(128, read_array_in, len(read_array_in)) <= 0
    assert not read_array_in.value
    read_array_in = create_string_buffer(64)
    assert rp1210.api.ReadMessage(0, read_array_in) <= 0
    assert not read_array_in.value
    assert not rp1210.api.ReadDirect(0)
    assert rp1210.api.ReadDetailedVersionDirect(0) == ("", "", "")

def test_disconnected_rp1210client_commands(apiname : str):
    """Tests RP1210Client command functions when adapter is disconnected."""
    client = RP1210.RP1210Client()
    client.setVendor(API_NAME)
    assert client.getClientID() == 128
    clientID = client.connect()
    assert clientID in RP1210.RP1210_ERRORS.keys()
    assert clientID == client.getClientID()
    # sampling of simpler commands
    assert client.resetDevice() in RP1210.RP1210_ERRORS.keys()
    assert client.setAllFiltersToPass() in RP1210.RP1210_ERRORS.keys()
    assert client.setAllFiltersToDiscard() in RP1210.RP1210_ERRORS.keys()
    assert client.setEcho(True) in RP1210.RP1210_ERRORS.keys()
    assert client.setMessageReceive(True) in RP1210.RP1210_ERRORS.keys()
    assert client.releaseJ1939Address(0xEE) in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939FilterType(0) in RP1210.RP1210_ERRORS.keys()
    assert client.setCANFilterType(0) in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939InterpacketTime(100) in RP1210.RP1210_ERRORS.keys()
    assert client.setMaxErrorMsgSize(100) in RP1210.RP1210_ERRORS.keys()
    assert client.disallowConnections() in RP1210.RP1210_ERRORS.keys()
    assert client.setJ1939Baud(5) in RP1210.RP1210_ERRORS.keys()
    assert client.setBlockingTimeout(20, 30) in RP1210.RP1210_ERRORS.keys()
    assert client.flushBuffers() in RP1210.RP1210_ERRORS.keys()
    assert client.setCANBaud(5) in RP1210.RP1210_ERRORS.keys()

'''
