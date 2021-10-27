from RP1210C import J1939, sanitize_msg_param

def test_format_default():
    assert J1939.getJ1939ProtocolString() == "J1939:Baud=Auto"

def test_format1():
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250) == "J1939:Baud=250"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto") == "J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=666, Channel=3) == "J1939:Baud=666,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud="Auto", Channel=3) == "J1939:Baud=Auto,Channel=3"
    assert J1939.getJ1939ProtocolString(protocol=1) == "J1939:Baud=Auto"
    assert J1939.getJ1939ProtocolString(protocol=1, Channel=2) == "J1939:Baud=Auto,Channel=2"
    assert J1939.getJ1939ProtocolString(protocol=1, Baud=250, SampleLocation=23, SJW=1, 
                                    PROP_SEG=4, PHASE_SEG1=4, PHASE_SEG2=3, TSEG1=53, 
                                    TSEG2=43, SampleTimes=5) == "J1939:Baud=250"

def test_format2():
    assert J1939.getJ1939ProtocolString(protocol=2) == "J1939"
    assert J1939.getJ1939ProtocolString(protocol=2, Channel=4) == "J1939,Channel=4"
    assert J1939.getJ1939ProtocolString(protocol=2, Baud=500) == "J1939"

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

def test_J1939MessageParser():
    """Test J1939MessageParser class"""

