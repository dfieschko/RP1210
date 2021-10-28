"""
Tests Noregon DLA 2.0 RP1210 functions with adapter connected to PC but not to
a device.

This is done on the DLA 2.0 adapter because it has the ability to be powered from
the PC's USB port.
"""
from RP1210C import J1939, RP1210
from tkinter import messagebox
import time

API_NAME = "DLAUSB32"

def test_dla2_drivers_begin():
    messagebox.showinfo("Connect your DLA2 adapter!", "Connect your DLA2 adapter, then hit OK to continue.")

def test_dla2_drivers_installed():
    assert API_NAME in RP1210.getAPINames()
    dla2 = RP1210.RP1210Interface(API_NAME)
    assert dla2.isValid()
    assert dla2.api.getDLL() != None
    assert dla2.api.isValid()

def test_ClientConnect():
    """Tests RP1210_ClientConnect with DLA 2.0 adapter connected."""
    dla2 = RP1210.RP1210Interface(API_NAME)
    deviceID = dla2.getDevices()[0]
    if dla2.CANAutoBaud():
        protocol_str = J1939.getJ1939ProtocolString(protocol=1, Baud="Auto")
    else:
        protocol_str = J1939.getJ1939ProtocolString(protocol=2)
    clientID = dla2.api.ClientConnect(deviceID, protocol_str)
    assert RP1210.translateErrorCode(clientID) == "NO_ERRORS"

def test_ClientConnect_overflow():
    dla2 = RP1210.RP1210Interface(API_NAME)
    deviceID = dla2.getDevices()[0]
    if dla2.CANAutoBaud():
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
    dla2 = RP1210.RP1210Interface(API_NAME)
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
    dla2 = RP1210.RP1210Interface(API_NAME)
    deviceID = dla2.getDevices()[0]
    # make sure we're disconnected
    for x in range (0, 15):
        dla2.api.ClientDisconnect(x)
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
        time.sleep(0.05)
        # disconnect
        disconnect_code = dla2.api.ClientDisconnect(clientID)
        assert RP1210.translateErrorCode(disconnect_code) == "NO_ERRORS"
        time.sleep(0.05)

