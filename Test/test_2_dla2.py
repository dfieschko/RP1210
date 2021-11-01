from RP1210C import RP1210, Commands
from ctypes import create_string_buffer

API_NAME = "DLAUSB32"

def test_RP1210Interface():
    """
    Tests the RP1210Interface class with Noregon DLA 2.0 drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.isValid() == True
    assert str(rp1210) == API_NAME + " - Noregon Systems Inc., DLA+ 2.0 Adapter"
    assert rp1210.getAPIName() == API_NAME
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
    assert rp1210.getProtocolIDs() == [51,52,53,54,55,56,58,59,60,61,62,63]

def test_Devices():
    """
    Tests the Device class with Noregon DLA 2.0 drivers.

    You must have these drivers installed to run this test.
    """
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    deviceIDs = rp1210.getDevices()
    assert deviceIDs == [100]
    device100 = rp1210.getDevice(100)
    assert device100.getID() == 100
    assert device100.getDescription() == "DLA+ 2.0, USB"
    assert device100.getName() == "DLA+ 2.0"
    assert device100.getParams() == "USB:CAN1:250"
    assert str(device100) == str(device100.getID()) + " - " + device100.getDescription()

def test_Protocols():
    assert API_NAME in RP1210.getAPINames()
    rp1210 = RP1210.RP1210Interface(API_NAME)
    protocolIDs = rp1210.getProtocolIDs()
    assert protocolIDs == [51,52,53,54,55,56,58,59,60,61,62,63]
    assert rp1210.getProtocols() == ["CAN", "J1939", "J1708", "IESCAN", "J1850", "J1850_104k", "ISO15765",
                                    "J2284", "ISO9141", "KWP2000", "KW2000", "NULL"]
    assert rp1210.getProtocol("J1939").getString() == "J1939"
    protocol1 = rp1210.getProtocol(51)
    assert protocol1.getDescription() == "CAN Network Protocol"
    assert protocol1.getString() == "CAN"
    assert protocol1.getParams() == ""
    assert protocol1.getDevices() == [100]
    assert protocol1.getSpeed() == ["125","250","500","666","1000","Auto"]
    protocol2 = rp1210.getProtocol(52)
    assert protocol2.getDescription() == "SAE J1939 Protocol"
    assert protocol2.getString() == "J1939"
    assert protocol2.getParams() == ""
    assert protocol2.getDevices() == [100]
    assert protocol2.getSpeed() == ["250","500","666","1000","Auto"]

def test_load_DLL():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.api.getDLL() != None
    rp12102 = RP1210.RP1210Interface(API_NAME)
    assert rp12102.api.loadDLL() != None

def test_disconnected_ClientConnect():
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    rp1210 = RP1210.RP1210Interface(API_NAME)
    clientID = rp1210.api.ClientConnect(100, b"J1939:Baud=Auto")
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
    assert buff1.value == b"4"
    assert buff2.value == b"0"
    assert buff3.value == b"4"
    assert buff4.value == b"0"

def test_disconnected_ReadVersionDirect():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    assert rp1210.api.ReadVersionDirect() == ("4.0", "4.0")

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
        # DLA2 also doesn't follow standard error codes, so we won't check them for correctness here.

def test_disconnected_SendCommand():
    rp1210 = RP1210.RP1210Interface(API_NAME)
    for command in Commands.RP1210_COMMANDS:
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
    assert rp1210.api.ReadDetailedVersionDirect(0) == ("4.0", "4.0.7445.1", "0")
