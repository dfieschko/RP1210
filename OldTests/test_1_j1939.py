from RP1210 import J1939, Commands, sanitize_msg_param
import binascii
import pytest

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

def test_toJ1939Message():
    """test toJ1939Message()"""
    pgn = 0x00FEEE
    pri = 3
    sa = 2
    da = 0x0E
    data = 0xDEADBEEF
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    data = b'\xDE\xAD\xBE\xEF'
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    dm1_data = b'\x72\x00\x31\x04\x5F\xE0'
    msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, dm1_data)
    assert msg ==b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
    pgn = 0x0AACCC
    pri = 0
    sa = 22
    da = 0x1E
    data = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF0000
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xCC\xAC\x0A\x00\x16\x1E\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\x00\x00'

def test_J1939Request():
    """Test toJ1939Request()"""
    sa = 2
    request = 0x00FEEE # engine temperature
    msg = J1939.toJ1939Request(request, sa)
    assert msg == b'\x00\xEA\x00\x06\x02\xFF\xEE\xFE\x00\x00\x00\x00\x00\x00'
    j1939msg = J1939.J1939Message(msg)
    assert j1939msg.getPGN() == 0x00EA00
    assert j1939msg.getSourceAddress() == 2
    assert j1939msg.getDestination() == 0xFF
    assert j1939msg.getPriority() == 6

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
    parser = J1939.J1939Message(message)
    assert parser.getTimestamp() == 0x01020304
    assert parser.getPGN() == pgn
    assert parser.getSource() == sa
    assert parser.getDestination() == da
    assert parser.getData() == sanitize_msg_param(data)

def test_J1939Message_2():
    timestamp = b'\x12\34\x56\x78'
    pgn = 0x00FEEE
    pri = 3
    sa = 2
    da = 0x0E
    data = 0xDEADBEEF
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    j1939 = J1939.J1939Message(timestamp + message)
    assert j1939.getTimestamp() == int.from_bytes(timestamp, 'big')
    assert j1939.getPGN() == pgn
    assert j1939.getPriority() == pri
    assert j1939.getSourceAddress() == sa
    assert j1939.getDestination() == da
    assert j1939.getData() == sanitize_msg_param(data)
    data = b'\xDE\xAD\xBE\xEF'
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xEE\xFE\x00\x03\x02\x0E\xDE\xAD\xBE\xEF'
    j1939 = J1939.J1939Message(timestamp + message)
    assert j1939.getTimestamp() == int.from_bytes(timestamp, 'big')
    assert j1939.getPGN() == pgn
    assert j1939.getPriority() == pri
    assert j1939.getSourceAddress() == sa
    assert j1939.getDestination() == da
    assert j1939.getData() == sanitize_msg_param(data)
    dm1_data = b'\x72\x00\x31\x04\x5F\xE0'
    msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, dm1_data)
    assert msg ==b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
    j1939 = J1939.J1939Message(timestamp + msg)
    assert j1939.getTimestamp() == int.from_bytes(timestamp, 'big')
    assert j1939.getPGN() == 0xFECA
    assert j1939.getPriority() == 6
    assert j1939.getSourceAddress() == 0x12
    assert j1939.getDestination() == 0xFF
    assert j1939.getData() == sanitize_msg_param(dm1_data)

def test_J1939Message_3():
    timestamp = b'\x01\x23\x45\x67'
    data = b'\x72\x00\x31\x04\x5F\xE0'
    msg = J1939.toJ1939Message(0xFECA, 6, 0x12, 0xFF, data)
    assert msg == b'\xCA\xFE\x00\x06\x12\xFF\x72\x00\x31\x04\x5F\xE0'
    j1939 = J1939.J1939Message(timestamp + msg)
    assert j1939.msg == timestamp + msg
    assert j1939.getPriority() == 6
    assert j1939.getPGN() == 0xFECA
    assert j1939.getDestination() == 0xFF
    assert j1939.getSource() == 0x12
    assert j1939.getData() == data

def test_J1939Message_long():
    timestamp = b'\x12\34\x56\x78'
    pgn = 0x0AACCC
    pri = 0
    sa = 22
    da = 0x1E
    data = 0xDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF0000
    message = J1939.toJ1939Message(pgn, pri, sa, da, data)
    assert message == b'\xCC\xAC\x0A\x00\x16\x1E\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\xDE\xAD\xBE\xEF\x00\x00'
    j1939 = J1939.J1939Message(timestamp + message)
    assert j1939.getTimestamp() == int.from_bytes(timestamp, 'big')
    assert j1939.getPGN() == pgn
    assert j1939.getPriority() == pri
    assert j1939.getSourceAddress() == sa
    assert j1939.getDestination() == da
    assert j1939.getData() == sanitize_msg_param(data)

def test_J1939MessageParser_Request():
    """Test J1939MessageParser class w/ a J1939 Request message."""
    timestamp = b'\x00\x00\x00\x00'
    msg = J1939.toJ1939Request(0XFEEE, 2)
    parser = J1939.J1939Message(timestamp + msg)
    assert parser.getTimestamp() == 0
    assert parser.isRequest() == True
    assert parser.getPGN() == 0x00EA00
    assert parser.getPriority() == 6
    assert parser.getSource() == 2
    assert parser.getDestination() == 255
    assert parser.getData() == b'\xEE\xFE\x00'
    assert parser.isEcho() == False

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

def test_setJ1939Filters():
    PGN = 1
    SOURCE = 4
    DEST = 8
    assert Commands.setJ1939Filters(0) == b'\x00\x00\x00\x00\x00\x00\x00'
    assert Commands.setJ1939Filters(PGN, pgn=0x0EF123) == b'\x01\x23\xF1\x0E\x00\x00\x00'
    assert Commands.setJ1939Filters(SOURCE, source=0xAB) == b'\x04\x00\x00\x00\x00\xAB\x00'
    assert Commands.setJ1939Filters(DEST, dest=0xCD) == b'\x08\x00\x00\x00\x00\x00\xCD'
    assert Commands.setJ1939Filters(PGN+SOURCE, pgn=0x0EF123, source=0xAB) == b'\x05\x23\xF1\x0E\x00\xAB\x00'

    filter_type = PGN # filter by PGN
    filter_list_int = [0xB100,
                    0xB200,
                    0xB300,
                    0xB400,
                    0xE000,
                    0xE04E,
                    0xE099,
                    0xE0FF,
                    0xF003,
                    0xF004,
                    0xFEDA,
                    0xFEEE,
                    0xFEF1,
                    0xFEF6,
                    0xFEF7,
                    0xFEF8,
                    0xFFCC,
                    0xFECA,
                    0x7500,
                    0x7800]
    filter_list_str = ["B100",
                       "B200",
                       "B300",
                       "B400",
                       "E000",
                       "E04E",
                       "E099",
                       "E0FF",
                       "F003",
                       "F004",
                       "FEDA",
                       "FEEE",
                       "FEF1",
                       "FEF6",
                       "FEF7",
                       "FEF8",
                       "FFCC",
                       "FECA",
                       "7500",
                       "7800"
                       ]
    for i in range(len(filter_list_int)):
        messageString = binascii.a2b_hex("01" + filter_list_str[i][2:4] + filter_list_str[i][0:2] + "00" + "000000")
        cmd_string = Commands.setJ1939Filters(filter_type, pgn=filter_list_int[i])
        assert messageString == cmd_string

@pytest.mark.skip("This test hasn't been implemented yet.")
def test_toJ1939Name():
    # arbitrary address (1 bit)
    # industry group (3 bits)
    # vehicle system instance (4 bits)
    # vehicle system (7 bits)
    # reserved bit (1 bit)
    # function (8 bits)
    # function instance (5 bits)
    # ecu instance (3 bits)
    # manufacturer code (11 bits)
    # identity number (21 bits)
    """TODO"""
    

def test_J1939MessageParser_isDM_hex():
    """
    Runs a simple test on all J1939MessageParser.isDMxxxx() functions w/ hex inputs
    """
    def makeMessage(pgn):
        # 4-byte timestamp
        msg = b'0000' + J1939.toJ1939Message(pgn, 3, 0xFE, pgn & 0xFF, b'Bingus')
        return J1939.J1939Message(msg)

    msg = makeMessage(0x1111)
    assert msg.getPGN() == 0x1111
    assert not msg.isDMRequest()
    assert not msg.isDM1()
    assert not msg.isDM2()
    assert not msg.isDM3()
    assert not msg.isDM4()
    assert not msg.isDM11()
    assert not msg.isDM12()

    assert makeMessage(0xEA00).isDMRequest()
    assert makeMessage(0xFECA).isDM1()
    assert makeMessage(0xFECB).isDM2()
    assert makeMessage(0xFECC).isDM3()
    assert makeMessage(0xFECD).isDM4()
    assert makeMessage(0xFED3).isDM11()
    assert makeMessage(0xFED4).isDM12()
