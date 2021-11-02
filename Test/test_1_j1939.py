from RP1210 import J1939, Commands, sanitize_msg_param

def test_format_default():
    assert J1939.getJ1939ProtocolString() == b"J1939:Baud=Auto"

def test_format1():
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250) == b"J1939:Baud=250"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto") == b"J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=666, Channel=3) == b"J1939:Baud=666,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto", Channel=3) == b"J1939:Baud=Auto,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1) == b"J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Channel=2) == b"J1939:Baud=Auto,Channel=2"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250, SampleLocation=23, SJW=1, 
                                    PROP_SEG=4, PHASE_SEG1=4, PHASE_SEG2=3, TSEG1=53, 
                                    TSEG2=43, SampleTimes=5) == b"J1939:Baud=250"

def test_format2():
    assert J1939.getJ1939ProtocolString(protocol=2) == b"J1939"
    assert J1939.getJ1939ProtocolString(protocol=2, Channel=4) == b"J1939,Channel=4"
    assert J1939.getJ1939ProtocolString(protocol=2, Baud=500) == b"J1939"

# I don't really care about protocol IDs 3 through 5 at the moment

def test_format_descriptions():
    assert J1939.getJ1939ProtocolDescription(1) == "Variable J1939 baud rate. Select 125, 250, 500, 1000, or Auto."
    assert J1939.getJ1939ProtocolDescription(2) == "General default for J1939 baud rate (250k baud)."
    assert J1939.getJ1939ProtocolDescription(3) == "Driver uses SampleLocation to calculate parameters."
    assert J1939.getJ1939ProtocolDescription(4) == "Baud formula derived from BOSCH CAN specification."
    assert J1939.getJ1939ProtocolDescription(5) == "Baud formula derived from Intel implementations."
    assert J1939.getJ1939ProtocolDescription(-1) == "Invalid J1939 protocol format selected."
    assert J1939.getJ1939ProtocolDescription(0) == "Invalid J1939 protocol format selected."
    assert J1939.getJ1939ProtocolDescription(6) == "Invalid J1939 protocol format selected."

def test_toJ1939Message_empty():
    """test toJ1939Message() with empty/null arguments"""
    assert J1939.toJ1939Message(0, 0, 0, 0, bytes(0)) == bytes(6)
    assert J1939.toJ1939Message(0, 0, 0, 0, b'') == bytes(6)
    assert J1939.toJ1939Message(b'', b'', b'', b'', b'') == bytes(6)
    assert J1939.toJ1939Message('', '', '', '', b'') == bytes(6)
    assert J1939.toJ1939Message('0', '0', '0', '0', b'') == bytes(6)

def test_toJ1939Message():
    """test toJ1939Message()"""
    pgn = 0x00FEEE
    pri = "3"
    sa = "2"
    da = 0x0E
    data = 0xDEADBEEF
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    pgn = 0x0AACCC
    pri = "0"
    sa = "22"
    da = 0x1E
    data = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF0000
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xCC\xAC\x0A\x00\x16\x1E\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\x00\x00'

def test_J1939Request():
    """Test toJ1939Request()"""
    sa = 2
    request = 0xFEEE # engine temperature
    msg = J1939.toJ1939Request(request, sa)
    assert msg == b'\x00\xEA\x00\x06\x02\xFF\xEE\xFE\x00'

def test_J1939MessageParser():
    """Test J1939MessageParser class"""
    timestamp = sanitize_msg_param(0x01020304)
    assert timestamp == b'\x01\x02\x03\x04'
    pgn = 0x00FEEE
    pri = 3
    sa = 2
    da = 0x0E
    data = 0xDEADBEEF
    message = timestamp + J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\x01\x02\x03\x04\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    parser = J1939.J1939MessageParser(message)
    assert parser.getTimestamp() == 0x01020304
    assert parser.getPGN() == pgn
    assert parser.getSource() == sa
    assert parser.getDestination() == da
    assert parser.getData() == sanitize_msg_param(data)

def test_J1939MessageParser_Request():
    """Test J1939MessageParser class w/ a J1939 Request message."""
    timestamp = b'\x00\x00\x00\x00'
    msg = J1939.toJ1939Request(0XFEEE, 2)
    parser = J1939.J1939MessageParser(timestamp + msg)
    assert parser.getTimestamp() == 0
    assert parser.isRequest() == True
    assert parser.getPGN() == 0x00EA00
    assert parser.getPriority() == 6
    assert parser.getSource() == 2
    assert parser.getDestination() == 255
    assert parser.getData() == b'\xEE\xFE\x00'

def test_command_claimAddress():
    address = 0x0F
    name = 0xDEADBEEF
    blocking = True
    command = Commands.protectJ1939Address(address, name, blocking)
    assert command == b"\x0F\x00\x00\x00\x00\xDE\xAD\xBE\xEF\x00"
    address = 1
    name = 2355321 # 0x23F079
    blocking = False
    command = Commands.protectJ1939Address(address, name, blocking)
    assert command == b"\x01\x00\x00\x00\x00\x00\x23\xF0\x79\x02"
