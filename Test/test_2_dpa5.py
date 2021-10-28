from RP1210C import RP1210
from ctypes import create_string_buffer

API_NAME = "DGDPA5MA"

def test_RP1210Interface():
    """
    Tests the RP1210Interface class with Dearborn DPA5 Pro drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.isValid() == True
    assert str(rp1210) == API_NAME + " - DG Technologies DPA 5 Multi Application"
    assert rp1210.getAPIName() == API_NAME
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
    assert rp1210.getProtocolIDs() == [100,101,102,103,104,105,106,107,108,109,110,111]

def test_Devices():
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    deviceIDs = rp1210.getDevices()
    assert deviceIDs == [1, 2]
    device1 = rp1210.getDevice(1)
    assert device1.getID() == 1
    assert device1.getDescription() == "DG DPA 5 Dual CAN (MA) USB,USB"
    assert device1.getName() == "DG DPA 5 Dual CAN (MA) USB"
    assert device1.getParams() == "DG USB,Type=3"
    assert device1.getMultiCANChannels() == 2
    assert device1.getMultiJ1939Channels() == 2
    assert str(device1) == str(device1.getID()) + " - " + device1.getDescription()
    device2 = rp1210.getDevice(2)
    assert device2.getID() == 2
    assert device2.getDescription() == "DG DPA 5 Pro (MA) USB,USB"
    assert device2.getName() == "DG DPA 5 Pro (MA) USB"
    assert device2.getParams() == "DG USB,Type=4"
    assert device2.getMultiCANChannels() == 4
    assert device2.getMultiJ1939Channels() == 4
    assert str(device2) == str(device2.getID()) + " - " + device2.getDescription()

def test_Protocols():
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    protocolIDs = rp1210.getProtocolIDs()
    assert protocolIDs == [100,101,102,103,104,105,106,107,108,109,110,111]
    assert rp1210.getProtocols() == ["J1939", "J1708", "CAN", "J1850_104K", "J1850_416K", "PLC", "ISO15765",
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

def test_load_DLL():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.api.getDLL() != None
    rp12102 = RP1210.RP1210Interface(API_NAME)
    assert rp12102.api.loadDLL() != None

def test_disconnected_ClientConnect():
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Interface(API_NAME)
    clientID = rp1210.api.ClientConnect(1, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in [ "ERR_OPENING_PORT", 
                                                    "ERR_HARDWARE_NOT_RESPONDING",
                                                    "ERR_INVALID_PROTOCOL"]

def test_disconnected_ClientDisconnect():
    """Tests whether ClientDisconnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Interface(API_NAME)
    code = rp1210.api.ClientDisconnect(0)
    assert code >= 128

def test_disconnected_ReadVersion():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    buff1 = create_string_buffer(16)
    buff2 = create_string_buffer(16)
    buff3 = create_string_buffer(16)
    buff4 = create_string_buffer(16)
    rp1210.api.ReadVersion(buff1, buff2, buff3, buff4)
    assert buff1.value == b"0"
    assert buff2.value == b"0"
    assert buff3.value == b"3"
    assert buff4.value == b"0"

def test_disconnected_ReadVersionDirect():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.api.ReadVersionDirect() == ("0.0", "3.0")

def test_disconnected_ReadDetailedVersion():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    buff1 = create_string_buffer(17)
    buff2 = create_string_buffer(17)
    buff3 = create_string_buffer(17)
    ret_val = rp1210.api.ReadDetailedVersion(0, buff1, buff2, buff3)
    assert RP1210.translateErrorCode(ret_val) in ["ERR_DLL_NOT_INITIALIZED", "ERR_HARDWARE_NOT_RESPONDING", "ERR_INVALID_CLIENT_ID"]

def test_disconnected_GetErrorMsg():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    for code in RP1210.RP1210_ERRORS:
        msg = rp1210.api.GetErrorMsg(code)
        # Dearborn DPA5 has nonstandard error codes - don't check against dict for correctness

def test_disconnected_SendCommand():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    for command in RP1210.RP1210_COMMANDS:
        assert rp1210.api.SendCommand(command, 0) in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatus():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    buffer = create_string_buffer(64)
    ret_val = rp1210.api.GetHardwareStatus(0, buffer, 64)
    assert not buffer.value
    assert ret_val in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatusDirect():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert not rp1210.api.GetHardwareStatusDirect(0).value

def test_disconnected_RemainingFunctions():
    """Tests whether API functions follow expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Interface(API_NAME)
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
    assert not rp1210.api.ReadDirect(0).value
    assert rp1210.api.ReadDetailedVersionDirect(0) == ("", "", "")
