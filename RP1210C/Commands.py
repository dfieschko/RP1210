"""
Generate ClientCommand inputs for RP1210_SendCommand.

Each function in this file returns a value that can be used for ClientCommand.
"""
from RP1210C import sanitize_msg_param

J1939_FILTERS = {
    "PGN" : 0x01,
    "SOURCE" : 0x04,
    "DEST" : 0x08,
    "DESTINATION" : 0x08
}
"""
A dict of valid J1939 filter parameters.

When using these as an argument for RP1210_Set_Message_Filtering_For_J1939,
you can add them together to filter for more than one at once.

Example (this will set the filter for both source and destination addresses):
    filter_flag = J1939_FILTERS["SOURCE"] + J1939_FILTERS["DEST"]

- "PGN"         => 1
- "SOURCE"      => 4
- "DEST"        => 8
- "DESTINATION" => 8
"""

CAN_TYPES = {
    "STANDARD_CAN" : 0x00,
    "EXTENDED_CAN" : 0x01,
    "STANDARD_CAN_IS015765_EXTENDED" : 0x02,
    "EXTENDED_CAN_IS015765_EXTENDED" : 0x03,
    "STANDARD_MIXED_CAN_IS015765" : 0x04
}
"""
A dict of CAN type codes, as defined in the RP1210C standard.
- "STANDARD_CAN" : 0x00
- "EXTENDED_CAN" : 0x01
- "STANDARD_CAN_IS015765_EXTENDED" : 0x02
- "EXTENDED_CAN_IS015765_EXTENDED" : 0x03
- "STANDARD_MIXED_CAN_IS015765" : 0x04
"""

def reset():
    """
    Reset Device (0) (0 bytes)

    Returns empty byte string (this command needs no extra data).
    """
    return b''

def setAllFiltersToPass():
    """
    Set All Filter States to Pass (3) (0 bytes)

    Returns empty byte string (this command needs no extra data).
    """
    return b''

def setJ1939Filters(filter_flag : int, pgn = 0, source = 0, dest = 0) -> bytes:
    """
    Set Message Filtering for J1939 (4) (7 bytes)

    Args:
    - Filter flag (1 byte) - filter flag integer/bytecode.
        - FILTER_PGN (1), FILTER_SOURCE (2), FILTER_DESTINATION (4)
        - J1939_FILTERS dict is available for convenience.
    - PGN (3 bytes) - the PGN that needs to be filtered.
    - Source Address (1 byte) - the source address that needs to be filtered.
    - Destination Address (1 byte) - the destination address that needs to be filtered.

    Args pgn, source, and dest only do anything if they are set with filter_flag. If they aren't,
    they will be ignored.

    You can specifiy filter_flag and keyword arguments instead of entering useless values for
    pgn, source, or dest.
        Example (this will filter for messages that come from 0x1E and sent to 0xB0):
            command = Commands.setJ1939Filters(4+8, source=0x1E, dest=0xB0)
    """
    ret_val = sanitize_msg_param(filter_flag, 1)
    ret_val += sanitize_msg_param(pgn, 3, 'little')
    ret_val += sanitize_msg_param(0, 1) # FILTER_PRIORITY was removed from RP1210 standard
    ret_val += sanitize_msg_param(source, 1)
    ret_val += sanitize_msg_param(dest, 1)
    return ret_val 


def setCANFilters(can_type, mask, header) -> bytes:
    """
    Set Message Filtering for CAN (5)

    Args:
    - CAN Type (1 byte) - 0x00 for STANDARD_CAN, 0x01 for EXTENDED_CAN.
        - See dict CAN_TYPES for other types.
    - Mask (4 bytes) - a bitwise mask that indicates which bits in the header need to be matched.
        - Big endian; "1" means a value is important; "0" means a value is unimportant.
    - Header (4 bytes) - "Indicates what value is required for each bit of interest".

    This is one of those functions that you're going to want the RP1210C documentation for.
    """
    ret_val = sanitize_msg_param(can_type, 1)
    ret_val += sanitize_msg_param(mask, 4)
    ret_val += sanitize_msg_param(header, 4)
    return ret_val

def generic():
    """
    Generic Driver Command (14) 
    """
    #TODO

def echoTx():
    """
    Set Echo Transmitted Messages (16)
    """
    #TODO

def setAllFiltersToDiscard():
    """
    Set All Filter States to Discard (17)
    """
    #TODO

def setMessageReceive():
    """
    Set Message Receive (18)
    """
    #TODO

def protectJ1939Address(address_to_claim, network_mgt_name, blocking = True):
    """
    Protect J1939 Address (19) (10 bytes)

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

def setCANBroadcastList():
    """
    Set Broadcast List for CAN (21)
    """
    #TODO

def setJ1939BroadcastList():
    """
    Set Broadcast List for J1939 (22)
    """
    #TODO

def setJ1939FilterType():
    """
    Set J1939 Filter Type (25)
    """
    #TODO

def setCANFilterType():
    """
    Set CAN Filter Type (26)
    """
    #TODO

def setJ1939InterpacketTime():
    """
    Set J1939 Broadcast Interpacket Timing (27)
    """
    #TODO

def setMaxErrorMsgSize():
    """
    Set Max Error Message Return Size (28)
    """
    #TODO

def disallowConnections():
    """
    Disallow Further Client Connections (29)
    """
    #TODO

def releaseJ1939Address():
    """
    Release a J1939 Address (31)
    """
    #TODO

def setJ1939Baud():
    """
    Set J1939 Baud Rate (37)
    """
    #TODO

def setBlockingTimeout():
    """
    Set Blocking Timeout (215)
    """
    #TODO

def flushRxTxBuffers():
    """
    Flush the Send/Receive Buffers (39)
    """
    #TODO

def getConnectionSpeed():
    """
    What Speed Did the VDA Connect? (45)
    """
    #TODO

def getWirelessState():
    """
    Is the VDA operating in a wireless mode? (48)
    """
    #TODO

def setCANBaud():
    """
    Set CAN Baud Rate (47)
    """
    #TODO
