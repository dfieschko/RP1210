"""
J1939 functions for use with RP1210 APIs. Note that this implementation is RP1210-specific - i.e.
if you try to generate J1939 messages to transmit directly onto a CANbus, these functions will fail!

While a dict of J1939 PGNs would be convenient, they are not provided here because the list is a
copyright of SAE.

J1939 functions:
- toJ1939Message
- getJ1939ProtocolString
- getJ1939ProtocolDescription

J1939 classes:
- J1939MessageParser
"""

from RP1210C import sanitize_msg_param
from RP1210C.RP1210 import RP1210API


def toJ1939Message(pgn, priority, source, destination, data, sanitize = True) -> bytes:
    """
    Converts args to J1939 message suitable for RP1210_SendMessage function.

    String arguments are read as base-10! If you want to provide an argument in base-16, do it as
    an int or byte string.

    RP1210_SendMessage J1939 format:
    - PGN (3 bytes)
    - Priority (1 byte)
    - Source Address (1 byte)
    - Destination Address (1 byte)
    - Message Data (0 - 1785 byes)

    Arguments can be strings, ints, or bytes. This function will decode UTF-8 characters in strings
    to base-10 ints, so don't provide it with letters or special characters. If you want to send it
    0xFF, send it as an int and not "FF".

    Set argument sanitize to False if you don't want to sanitize arguments. This means
    you must provide them as bytes, but might save a bit of CPU time.
    """
    # sanitize inputs ~ convert to bytes
    if sanitize:
        pgn = sanitize_msg_param(pgn, 3, 'little')
        priority = sanitize_msg_param(priority, 1)
        source = sanitize_msg_param(source, 1)
        destination = sanitize_msg_param(destination, 1)
        data = sanitize_msg_param(data)
    return pgn + priority + source + destination + data

def toJ1939Request(pgn_requested, source, destination = 255, priority = 6):
    """
    Formats a J1939 request message. This puts out a request for the specified PGN, and will prompt
    other devices on the network to respond.

    - pgn_requested: the parameter group you're requesting
    - source: the source address, e.g. your address on the CANBus
    - destination: 255 = global request; enter a different number to request from a specific address
    - priority: priority of request; default is 6
    """
    pgn_request = sanitize_msg_param(pgn_requested, 3, 'little') # must be little-endian
    return toJ1939Message(0x00EA00, priority, source, destination, pgn_request)

def getJ1939ProtocolString(protocol = 1, Baud = "Auto", Channel = -1,
                        SampleLocation = 95, SJW = 1,
                        PROP_SEG = 1, PHASE_SEG1 = 2, PHASE_SEG2 = 1,
                        TSEG1 = 2, TSEG2 = 1, SampleTimes = 1) -> str:
    """
    Generates fpchProtocol string for ClientConnect function. The default values you see above
    were made up on the spot and shouldn't necessarily be used.

    Keyword arguments have the same names as below (e.g. Baud, SampleLocation, PHASE_SEG1).

    IDSize is automatically set to 29 whenever relevant because that is its only valid value.

    This function also accepts a Channel argument!

    Examples:
    - protocol1 = J1939.getProtocolString(protocol = 1, Baud = "Auto")
    - protocol2 = J1939.getProtocolString(protocol = 3, Baud = 500, SampleLocation = 75, SJW = 3, IDSize = 29)
    """
    if Channel != -1:
        chan_arg = f",Channel={str(Channel)}"
    else:
        chan_arg = ""

    if protocol == 1:
        return bytes(f"J1939:Baud={str(Baud)}" + chan_arg, 'utf-8')
    elif protocol == 2:
        return bytes("J1939" + chan_arg, 'utf-8')
    elif protocol == 3:
        return bytes(f"J1939:Baud={str(Baud)},SampleLocation={str(SampleLocation)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    elif protocol == 4:
        return bytes(f"J1939:Baud={str(Baud)},PROP_SEG={str(PROP_SEG)},PHASE_SEG1={str(PHASE_SEG1)},PHASE_SEG2={str(PHASE_SEG2)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    elif protocol == 5:
        return bytes(f"J1939:Baud={str(Baud)},TSEG1={str(TSEG1)},TSEG2={str(TSEG2)},SampleTimes={str(SampleTimes)},SJW={str(SJW)},IDSize=29" + chan_arg, 'utf-8')
    else:
        return b"J1939" # default to protocol format 2, default channel

def getJ1939ProtocolDescription(protocol : int) -> str:
    """Returns a description of the protocol selected with protocol arg."""
    if protocol == 1:
        return "Variable J1939 baud rate. Select 125, 250, 500, 1000, or Auto."
    elif protocol == 2:
        return "General default for J1939 baud rate (250k baud)."
    elif protocol == 3:
        return "Driver uses SampleLocation to calculate parameters."
    elif protocol == 4:
        return "Baud formula derived from BOSCH CAN specification."
    elif protocol == 5:
        return "Baud formula derived from Intel implementations."
    else:
        return "Invalid J1939 protocol format selected."

class J1939MessageParser():
    """
    A convenience class for parsing a J1939 message received from RP1210_ReadMessage.

    Message must include timestamp (4 bytes) in its leading bytes (this conforms w/ return value
    of RP1210_ReadMessage).

    - Initialize the object with the message received from ReadMessage.
    - If you used the command 'Set Echo Transmitted Messages' to turn echo on, set arg echo = True.
    """
    def __init__(self, j1939_message : bytes, echo = False) -> None:
        self.msg = j1939_message
        self.echo_offset = int(echo)

    def isEcho(self) -> bool:
        """Returns True if the message is an echo of a message you transmitted, False if not."""
        if self.echo_offset == 1:
            return int.from_bytes(self.msg[4]) == 0x01
        return False

    def isRequest(self) -> bool:
        """Returns true if PGN matches J1939 Request PGN."""
        return self.getPGN() == 0x00EA00

    def getTimestamp(self) -> int:
        """Returns timestamp (4 bytes) as int."""
        print(self.msg)
        print(self.msg[0:4])
        return int.from_bytes(self.msg[0:4], 'big')

    def getPGN(self) -> int:
        """Returns PGN (3 bytes) as int."""
        start = 4 + self.echo_offset
        end = 6 + self.echo_offset
        return int.from_bytes(self.msg[start:end], 'little')

    def getPriority(self) -> int:
        """Returns Priority (1 byte) as int."""
        loc = 7 + self.echo_offset
        return self.msg[loc]

    def getSource(self) -> int:
        """Returns Source Address (1 byte) as int."""
        loc = 8 + self.echo_offset
        return self.msg[loc]

    def getDestination(self) -> int:
        """Returns Destination Address (1 byte) as int."""
        loc = 9 + self.echo_offset
        return self.msg[loc]

    def getData(self) -> bytes:
        """Returns message data (0 - 1785 bytes) as bytes."""
        loc = 10 + self.echo_offset
        return self.msg[loc:]

# class J1939API(RP1210API):
#     """Child of RP1210API w/ J1939-specific functions."""

class J1939Commands:
    """
    Generate ClientCommand inputs for RP1210_SendCommand.
    """
    def claimAddress(self, address_to_claim, network_mgt_name, blocking = True):
        """
        This command claims an address on the J1939 bus.
        - address_to_claim (1 byte) - 8-bit address to claim on the J1939 bus.
        - network_mgt_name (8 bytes) - 8-byte name of client on network (this is you!)
            - See J1939 network management standard!
            - Lowest name takes priority if two devices try to claim the same address
        - blocking (bool) - True will block until done, False will return before completion

        This function automatically sanitizes str, int, and bytes inputs. str are parsed as 10-bit
        decimals! Use byte strings (b"message") if you want to pass utf-8 characters.
        """
        addr = sanitize_msg_param(address_to_claim, 1)
        name = sanitize_msg_param(network_mgt_name, 8)
        if blocking:
            status = sanitize_msg_param(0, 1) # BLOCK_UNTIL_DONE
        else:
            status = sanitize_msg_param(2, 1) # RETURN_BEFORE_COMPLETION
        return addr + name + status
        