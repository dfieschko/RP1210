"""
Tests Noregon DLA 2.0 RP1210 functions with adapter connected to PC but not to
a device.

This is done on the DLA 2.0 adapter because it has the ability to be powered from
the PC's USB port.
"""
from RP1210 import J1939, Commands
import RP1210
from tkinter import messagebox

TEST_ENABLED = False

def disconnect():
    api = RP1210.RP1210API(API_NAME)
    for clientID in range(0, 15):
        api.ClientDisconnect(clientID)

API_NAME = "DLAUSB32"

def test_dla2_drivers_begin():
    if not TEST_ENABLED:
        return
    messagebox.showinfo("Connect your DLA2 adapter!", 
                        "Connect your DLA2 adapter, then hit OK to continue.\nDon't connect the adapter to a CAN bus!")


# DON'T ADD ANY TESTS BEFORE THIS POINT!

def test_reset():
    if not TEST_ENABLED:
        return
    disconnect()
    api = RP1210.RP1210API(API_NAME)
    clientID = api.ClientConnect(100, b"J1939:Baud=500")
    ret_val = api.SendCommand(0, clientID)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"

def test_reset_too_many_connections():
    if not TEST_ENABLED:
        return
    disconnect()
    api = RP1210.RP1210API(API_NAME)
    clientID = api.ClientConnect(100, b"J1939:Baud=500")
    api.ClientConnect(100, b"J1939:Baud=500")
    ret_val = api.SendCommand(0, clientID)
    assert RP1210.translateErrorCode(ret_val) == "ERR_MULTIPLE_CLIENTS_CONNECTED"

def test_dla2_drivers_installed():
    if not TEST_ENABLED:
        return
    assert API_NAME in RP1210.getAPINames()
    dla2 = RP1210.RP1210Config(API_NAME)
    assert dla2.isValid()
    assert dla2.api.getDLL() != None
    assert dla2.api.isValid()

def test_ClientConnect():
    """Tests RP1210_ClientConnect with DLA 2.0 adapter connected."""
    if not TEST_ENABLED:
        return
    dla2 = RP1210.RP1210Config(API_NAME)
    deviceID = dla2.getDeviceIDs()[0]
    if dla2.getCANAutoBaud():
        protocol_str = J1939.getJ1939ProtocolString(protocol=1, Baud="Auto")
    else:
        protocol_str = J1939.getJ1939ProtocolString(protocol=2)
    clientID = dla2.api.ClientConnect(deviceID, protocol_str)
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"

def test_ClientConnect_overflow():
    if not TEST_ENABLED:
        return
    dla2 = RP1210.RP1210Config(API_NAME)
    deviceID = dla2.getDeviceIDs()[0]
    if dla2.getCANAutoBaud():
        protocol_str = J1939.getJ1939ProtocolString(protocol=1, Baud="Auto")
    else:
        protocol_str = J1939.getJ1939ProtocolString(protocol=2)
    for x in range(1, 12):
        clientID = dla2.api.ClientConnect(deviceID, protocol_str)
        assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    for x in range(1, 8):
        clientID = dla2.api.ClientConnect(deviceID, protocol_str)
        assert RP1210.translateErrorCode(clientID) in ["NO_ERRORS", "ERR_CLIENT_AREA_FULL"]
    
def test_ClientDisconnect():
    """This test calls RP1210_ClientDisconnect for each of the ClientConnect attempts in the test above."""
    if not TEST_ENABLED:
        return
    dla2 = RP1210.RP1210Config(API_NAME)
    for x in range (0, 12):
        ret_val = dla2.api.ClientDisconnect(x)
        assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    for x in range (13, 20):
        ret_val = dla2.api.ClientDisconnect(x)
        assert RP1210.translateErrorCode(ret_val) in ["NO_ERRORS", "ERR_INVALID_CLIENT_ID"] 

def test_ClientConnect_Disconnect_j1939_speeds():
    """
    Tests ClientConnect and ClientDisconnect with all possible J1939 speeds.
    """
    if not TEST_ENABLED:
        return
    dla2 = RP1210.RP1210Config(API_NAME)
    deviceID = dla2.getDeviceIDs()[0]
    # make sure we're disconnected
    disconnect()
    # get valid baud rates
    speeds = dla2.getProtocol("J1939").getSpeed()
    assert speeds == ["250", "500", "666", "1000", "Auto"]
    # cycle through all baud rates
    for speed in speeds:
        # generate protocol string
        protocol = J1939.getJ1939ProtocolString(protocol=1, Baud=speed)
        # connect
        clientID = dla2.api.ClientConnect(deviceID, protocol)
        assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
        assert clientID in [0, 1]
        # disconnect
        disconnect_code = dla2.api.ClientDisconnect(clientID)
        assert RP1210.translateErrorCode(disconnect_code) == "NO_ERRORS"

def test_SendMessage_no_address_claimed():
    """Tests SendMessage function while DLA2 connector is connected to PC but not an external device."""
    if not TEST_ENABLED:
        return
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    protocol = J1939.getJ1939ProtocolString(1, "500")
    data = b"This is a test message!"
    message = J1939.toJ1939Message(1234, 4, 10, 255, data)
    # connect
    clientID = api.ClientConnect(deviceID, protocol)
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    # send message w/o claiming address
    ret_val = api.SendMessage(clientID, message)
    assert RP1210.translateErrorCode(ret_val) == "ERR_ADDRESS_NEVER_CLAIMED"
    api.ClientDisconnect(clientID)

def test_SendCommand_claim_j1939_address():
    """Test SendCommand function w/ command "Protect_J1939_Address" (19)"""
    if not TEST_ENABLED:
        return
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    command_id = 19
    address = 10
    name = 24
    command_params = Commands.protectJ1939Address(address, name)
    assert len(command_params) == 10
    # make sure we're disconnected
    disconnect()
    # connect to adapter
    clientID = api.ClientConnect(deviceID, b"J1939:Baud=500")
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    # send command
    ret_val = api.SendCommand(command_id, clientID, command_params)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    api.ClientDisconnect(clientID)

def test_SendCommand_claim_and_release_j1939_address():
    if not TEST_ENABLED:
        return
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    command_id = 19
    address = 10
    name = 24
    command_params = Commands.protectJ1939Address(address, name)
    assert len(command_params) == 10
    # make sure we're disconnected
    disconnect()
    # connect to adapter
    clientID = api.ClientConnect(deviceID, b"J1939:Baud=500")
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    # send claim command
    ret_val = api.SendCommand(command_id, clientID, command_params)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    # release command
    command_params = Commands.releaseJ1939Address(address)
    command_id = Commands.COMMAND_IDS["RELEASE_J1939_ADDRESS"]
    ret_val = api.SendCommand(command_id, clientID, command_params)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    api.ClientDisconnect(clientID)

def test_SendCommand_release_unclaimed_j1939_address():
    if not TEST_ENABLED:
        return
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    address = 10
    # make sure we're disconnected
    disconnect()
    # connect to adapter
    clientID = api.ClientConnect(deviceID, b"J1939:Baud=500")
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    # release command
    command_params = Commands.releaseJ1939Address(address)
    command_id = Commands.COMMAND_IDS["RELEASE_J1939_ADDRESS"]
    ret_val = api.SendCommand(command_id, clientID, command_params)
    assert RP1210.translateErrorCode(ret_val) == "ERR_ADDRESS_RELEASE_FAILED"
    api.ClientDisconnect(clientID)

def test_SendMessage():
    """Tests SendMessage function while DLA2 connector is connected to PC but not an external device."""
    if not TEST_ENABLED:
        return
    disconnect()
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    protocol = J1939.getJ1939ProtocolString(1, "500")
    # connect
    clientID = api.ClientConnect(deviceID, protocol)
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"
    # claim address 10 w/ name 0xDEADBEEF
    command_msg = Commands.protectJ1939Address(10, 0xDEADBEEF)
    ret_val = api.SendCommand(19, clientID, command_msg)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    # send message
    data = b"This is a test message!"
    message = J1939.toJ1939Message(1234, 4, 10, 255, data)
    ret_val = api.SendMessage(clientID, message)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    api.ClientDisconnect(clientID)

def test_setMessageReceive():
    if not TEST_ENABLED:
        return
    api = RP1210.RP1210API(API_NAME)
    deviceID = 100
    protocol = J1939.getJ1939ProtocolString(1, "500")
    disconnect()
    # connect
    clientID = api.ClientConnect(deviceID, protocol)
    # command id and command data
    cmd_id = Commands.COMMAND_IDS["SET_MESSAGE_RECEIVE"]
    assert cmd_id == 18
    cmd_data = Commands.setMessageReceive(True)
    # test with valid clientID
    ret_val = api.SendCommand(cmd_id, clientID, cmd_data)
    assert RP1210.translateErrorCode(ret_val) == "NO_ERRORS"
    # test with invalid clientID
    ret_val = api.SendCommand(cmd_id, 255, cmd_data)
    assert RP1210.translateErrorCode(ret_val) == "ERR_INVALID_CLIENT_ID"
