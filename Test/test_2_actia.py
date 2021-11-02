from ctypes import create_string_buffer
from RP1210C import RP1210, Commands

API_NAME = "IMBRP32"

def test_RP1210Interface():
    """
    Tests the RP1210Interface class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.isValid() == True
    assert str(rp1210) == API_NAME + " - I+ME ACTIA GmbH"
    assert rp1210.getAPIName() == API_NAME
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
    assert rp1210.getVersion() == ""
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
    assert rp1210.getDeviceIDs() == [1, 2, 3]
    assert rp1210.getProtocolIDs() == [1, 2, 3]
    assert rp1210.getProtocols() == ["CAN", "J1708", "J1939"]

def test_Devices():
    """
    Tests the Device class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    deviceIDs = rp1210.getDeviceIDs()
    assert deviceIDs == [1, 2, 3]
    device1 = rp1210.getDevice(1)
    assert device1.getID() == 1
    assert device1.getDescription() == "BasicXS, USB"
    assert device1.getName() == "BasicXS USB"
    assert device1.getParams() == ""
    assert str(device1) == str(device1.getID()) + " - " + device1.getDescription()
    device2 = rp1210.getDevice(2)
    assert device2.getID() == 2
    assert device2.getDescription() == "BasicXS, COM1"
    assert device2.getName() == "BasicXS COM1"
    assert device2.getParams() == ""
    assert str(device2) == str(device2.getID()) + " - " + device2.getDescription()
    device3 = rp1210.getDevice(3)
    assert device3.getID() == 3
    assert device3.getDescription() == "BasicXS, COM2"
    assert device3.getName() == "BasicXS COM2"
    assert device3.getParams() == ""
    assert str(device3) == str(device3.getID()) + " - " + device3.getDescription()

def test_Protocols():
    """
    Tests the Device class with ACTIA BasicXS drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Config(API_NAME)
    protocolIDs = rp1210.getProtocolIDs()
    assert protocolIDs == [1, 2, 3]
    assert rp1210.getProtocols() == ["CAN", "J1708", "J1939"]
    assert rp1210.getProtocol("J1939").getString() == "J1939"
    protocol1 = rp1210.getProtocol(1)
    assert protocol1.getDescription() == "Generic CAN"
    assert protocol1.getString() == "CAN"
    assert protocol1.getParams() == ""
    assert protocol1.getDevices() == [1, 2, 3]
    assert protocol1.getSpeed() == []
    protocol2 = rp1210.getProtocol(2)
    assert protocol2.getDescription() == "J1708 Link Layer Protocol"
    assert protocol2.getString() == "J1708"
    assert protocol2.getParams() == ""
    assert protocol2.getDevices() == [1, 2, 3]
    assert protocol2.getSpeed() == []
    protocol3 = rp1210.getProtocol(3)
    assert protocol3.getDescription() == "J1939 Link Layer Protocol"
    assert protocol3.getString() == "J1939"
    assert protocol3.getParams() == ""
    assert protocol3.getDevices() == [1, 2, 3]
    assert protocol3.getSpeed() == []

def test_load_DLL():
    """
    Tests whether the ACTIA BasicXS+ DLL can be loaded.
    """
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.getDLL() != None
    rp12102 = RP1210.RP1210Config(API_NAME)
    assert rp12102.api.loadDLL() != None

def test_disconnected_ClientConnect():
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Config(API_NAME)
    clientID = rp1210.api.ClientConnect(1, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in [ "ERR_OPENING_PORT", 
                                                    "ERR_HARDWARE_NOT_RESPONDING",
                                                    "ERR_INVALID_PROTOCOL"]
    clientID = rp1210.api.ClientConnect(1, b"J1939")
    assert RP1210.translateErrorCode(clientID) in ["ERR_OPENING_PORT", 
                                                    "ERR_HARDWARE_NOT_RESPONDING"]

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
    assert buff1.value == b"1"
    assert buff2.value == b"0"
    assert buff3.value == b"2"
    assert buff4.value == b"0"

def test_disconnected_ReadVersionDirect():
    rp1210 = RP1210.RP1210Config(API_NAME)
    assert rp1210.api.ReadVersionDirect() == ("1.0", "2.0")

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
        assert msg in RP1210.RP1210_ERRORS.values() or msg == "ERR_ISO15765_BAUD_SET_NONSTANDARD" # doesn't recognize this in dict for some reason

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
    assert not rp1210.api.ReadDirect(0).value
    assert rp1210.api.ReadDetailedVersionDirect(0) == ("", "", "")
