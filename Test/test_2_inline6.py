import RP1210
from ctypes import create_string_buffer

API_NAME = "CMNSI632"

def test_RP1210Interface():
    """
    Tests the RP1210Interface class with Cummins Inline 6 drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.isValid() == True
    assert str(rp1210) == API_NAME + " - Cummins Inc. INLINE6"
    assert rp1210.getAPIName() == API_NAME
    assert rp1210.getName() == "Cummins Inc. INLINE6"
    assert rp1210.getAddress1() == "1460 N National Rd"
    assert rp1210.getAddress2() == ""
    assert rp1210.getCity() == "Columbus"
    assert rp1210.getState() == "IN"
    assert rp1210.getCountry() == "USA"
    assert rp1210.getPostal() == "47201"
    assert rp1210.getTelephone() == ""
    assert rp1210.getFax() == ""
    assert rp1210.getVendorURL() == "http://inline.cummins.com"
    assert rp1210.getVersion() == ""
    assert rp1210.autoDetectCapable() == False
    assert rp1210.CANAutoBaud() == True
    assert rp1210.getTimeStampWeight() == 1000
    assert rp1210.getMessageString() == "CMNSI632_RP1210_MSG"
    assert rp1210.getErrorString() == "CMNSI632_RP1210_ERROR"
    assert rp1210.getRP1210Version() == "B"
    assert rp1210.getDebugLevel() == 0
    assert rp1210.getDebugFile() == "C:\\ProgramData\\Cummins\\Inline6\\Debuglog.txt"
    assert rp1210.getDebugMode() == 1
    assert rp1210.getDebugFileSize() == 1024
    assert rp1210.getNumberOfSessions() == 1
    assert rp1210.getCANFormatsSupported() == [4,5]
    assert rp1210.getJ1939FormatsSupported() == [1,2]
    assert rp1210.getDeviceIDs() == [1,2,3,4,5,6,7,8,254,255]
    assert rp1210.getProtocolIDs() == [1,2,3,4]

def test_Devices():
    """
    Tests the Device class with Cummins Inline 6 drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    deviceIDs = rp1210.getDeviceIDs()
    assert deviceIDs == [1,2,3,4,5,6,7,8,254,255]
    device = rp1210.getDevice(1)
    assert device.getID() == 1
    assert device.getDescription() == "INLINE6,COM1"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(2)
    assert device.getID() == 2
    assert device.getDescription() == "INLINE6,COM2"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(3)
    assert device.getID() == 3
    assert device.getDescription() == "INLINE6,COM3"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(4)
    assert device.getID() == 4
    assert device.getDescription() == "INLINE6,COM4"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(5)
    assert device.getID() == 5
    assert device.getDescription() == "INLINE6,COM5"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(6)
    assert device.getID() == 6
    assert device.getDescription() == "INLINE6,COM6"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(7)
    assert device.getID() == 7
    assert device.getDescription() == "INLINE6,COM7"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(8)
    assert device.getID() == 8
    assert device.getDescription() == "INLINE6,COM8"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    device = rp1210.getDevice(254)
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    assert device.getID() == 254
    assert device.getDescription() == "INLINE6,USB"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()
    device = rp1210.getDevice(255)
    assert device.getID() == 255
    assert device.getDescription() == "INLINE6,COM Port Auto Detect"
    assert device.getName() == "INLINE6"
    assert device.getParams() == ""
    assert device.getMultiJ1939Channels() == 2
    assert device.getMultiCANChannels() == 2
    assert str(device) == str(device.getID()) + " - " + device.getDescription()

def test_Protocols():
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    protocolIDs = rp1210.getProtocolIDs()
    assert protocolIDs == [1,2,3,4]
    assert rp1210.getProtocols() == ["ISO15765", "J1939", "J1708", "CAN"]
    assert rp1210.getProtocol("J1939").getString() == "J1939"
    protocol = rp1210.getProtocol(1)
    assert protocol.getDescription() == "ISO15765"
    assert protocol.getString() == "ISO15765"
    assert protocol.getParams() == ""
    assert protocol.getDevices() == [1,2,3,4,5,6,7,8,254,255]
    assert protocol.getSpeed() == ["250","500","Auto"]
    protocol = rp1210.getProtocol(2)
    assert protocol.getDescription() == "J1939"
    assert protocol.getString() == "J1939"
    assert protocol.getParams() == ""
    assert protocol.getDevices() == [1,2,3,4,5,6,7,8,254,255]
    assert protocol.getSpeed() == ["250","500","Auto"]
    protocol = rp1210.getProtocol(3)
    assert protocol.getDescription() == "J1708"
    assert protocol.getString() == "J1708"
    assert protocol.getParams() == ""
    assert protocol.getDevices() == [1,2,3,4,5,6,7,8,254,255]
    assert protocol.getSpeed() == ["9600"]
    protocol = rp1210.getProtocol(4)
    assert protocol.getDescription() == "CAN"
    assert protocol.getString() == "CAN"
    assert protocol.getParams() == ""
    assert protocol.getDevices() == [1,2,3,4,5,6,7,8,254,255]
    assert protocol.getSpeed() == ["250","500","Auto"]

def test_load_DLL():
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.getDLL() != None
    rp12102 = RP1210.RP1210Config(API_NAME)
    assert rp12102.api.loadDLL() != None

def test_disconnected_ClientConnect():
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    clientID = rp1210.api.ClientConnect(100, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in [ "ERR_OPENING_PORT", 
                                                    "ERR_HARDWARE_NOT_RESPONDING",
                                                    "ERR_INVALID_PROTOCOL",
                                                    "ERR_DLL_NOT_INITIALIZED"]

def test_disconnected_ClientDisconnect():
    """Tests whether ClientDisconnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    code = rp1210.api.ClientDisconnect(0)
    assert code >= 128

def test_disconnected_ReadVersion():
    rp1210 = RP1210.RP1210Config(API_NAME)
    buff1 = create_string_buffer(16)
    buff2 = create_string_buffer(16)
    buff3 = create_string_buffer(16)
    buff4 = create_string_buffer(16)
    rp1210.api.ReadVersion(buff1, buff2, buff3, buff4)
    assert buff1.value == b":"
    assert buff2.value == b"1"
    assert buff3.value == b"3"
    assert buff4.value == b"0"

def test_disconnected_ReadVersionDirect():
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.ReadVersionDirect() == (":.1", "3.0")

def test_disconnected_ReadDetailedVersion():
    rp1210 = RP1210.RP1210Config(API_NAME)
    buff1 = create_string_buffer(17)
    buff2 = create_string_buffer(17)
    buff3 = create_string_buffer(17)
    ret_val = rp1210.api.ReadDetailedVersion(0, buff1, buff2, buff3)
    assert RP1210.translateErrorCode(ret_val) in ["ERR_DLL_NOT_INITIALIZED", "ERR_HARDWARE_NOT_RESPONDING", "ERR_INVALID_CLIENT_ID"]

def test_disconnected_GetErrorMsg():
    rp1210 = RP1210.RP1210Config(API_NAME)
    for code in RP1210.RP1210_ERRORS:
        msg = rp1210.api.GetErrorMsg(code)
        # DLA2 also doesn't follow standard error codes, so we won't check them for correctness here.

def test_disconnected_SendCommand():
    rp1210 = RP1210.RP1210Config(API_NAME)
    for command in RP1210.RP1210_COMMANDS:
        assert rp1210.api.SendCommand(command, 0) in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatus():
    rp1210 = RP1210.RP1210Config(API_NAME)
    buffer = create_string_buffer(64)
    ret_val = rp1210.api.GetHardwareStatus(0, buffer, 64)
    assert not buffer.value
    assert ret_val in RP1210.RP1210_ERRORS

def test_disconnected_GetHardwareStatusDirect():
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert not rp1210.api.GetHardwareStatusDirect(0).value

def test_disconnected_RemainingFunctions():
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
