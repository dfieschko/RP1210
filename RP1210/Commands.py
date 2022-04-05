"""
Generate ClientCommand inputs for RP1210_SendCommand.

Each function in this file returns a value that can be used for ClientCommand.
"""
from typing import Literal
from RP1210 import sanitize_msg_param

COMMAND_IDS = {
    "RESET_DEVICE" : 0,
    "SET_ALL_FILTERS_STATES_TO_PASS" : 3,
    "SET_MESSAGE_FILTERING_FOR_J1939" : 4,
    "SET_MESSAGE_FILTERING_FOR_CAN" : 5,
    "SET_MESSAGE_FILTERING_FOR_J1708" : 7,
    "SET_MESSAGE_FILTERING_FOR_J1850" : 8,
    "SET_MESSAGE_FILTERING_FOR_ISO15765" : 9,
    "GENERIC_DRIVER_COMMAND" : 14,
    "SET_J1708_MODE" : 15,
    "ECHO_TRANSMITTED_MESSAGES" : 16,
    "SET_ALL_FILTERS_STATES_TO_DISCARD" : 17,
    "SET_MESSAGE_RECEIVE" : 18,
    "PROTECT_J1939_ADDRESS" : 19,
    "SET_BROADCAST_FOR_J1708" : 20,
    "SET_BROADCAST_FOR_CAN" : 21,
    "SET_BROADCAST_FOR_J1939" : 22,
    "SET_BROADCAST_FOR_J1850" : 23,
    "SET_J1708_FILTER_TYPE" : 24,
    "SET_J1939_FILTER_TYPE" : 25,
    "SET_CAN_FILTER_TYPE" : 26,
    "SET_J1939_INTERPACKET_TIME" : 27,
    "SET_MAX_ERROR_MSG_SIZE" : 28,
    "DISALLOW_FURTHER_CONNECTIONS" : 29,
    "SET_J1850_FILTER_TYPE" : 30,
    "RELEASE_J1939_ADDRESS" : 31,
    "SET_ISO15765_FILTER_TYPE" : 32,
    "SET_BROADCAST_FOR_ISO15765" : 33,
    "SET_ISO15765_FLOW_CONTROL" : 34,
    "CLEAR_ISO15765_FLOW_CONTROL" : 35,
    "SET_J1939_BAUD" : 37,
    "SET_ISO15765_BAUD" : 38,
    "SET_BLOCKTIMEOUT" : 215,
    "SET_J1708_BAUD" : 305,
    "FLUSH_TX_RX_BUFFERS" : 39,
    "SET_BROADCAST_FOR_KWP2000" : 41,
    "SET_BROADCAST_FOR_ISO9141" : 42,
    "GET_PROTOCOL_CONNECTION_SPEED" : 45,
    "SET_ISO9141KWP2000_MODE" : 46,
    "SET_CAN_BAUD" : 47,
    "GET_WIRELESS_STATE" : 48}
"""
Mnemonics for RP1210_SendCommand commands. Follows ordering of table in section 21.4.

key:item orders are swapped from RP1210_COMMANDS in RP1210.py.

Example:
    command_id = Commands.COMMAND_IDS["PROTECT_J1939_ADDRESS"]
"""

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

ECHO_MODES = {
    "ECHO_OFF" : 0x00,
    "ECHO_ON" : 0x01
}
"""
Dict for echo modes, used in commmand ECHO_TRANSMITTED_MESSAGES (echoTx())

- ECHO_OFF : 0x00
- ECHO_ON : 0x01
"""

RECEIVE_MODES = {
    "RECEIVE_ON" : 0x01,
    "RECEIVE_OFF" : 0x00
}
"""
Dict for receive modes, used in command SET_MESSAGE_RECEIVE
- RECEIVE_ON : 0x01
- RECEIVE_ OFF : 0x00
"""

BROADCAST_FUNCTIONS = {
    "ADD_LIST" : 1,
    "VIEW_LIST" : 2,
    "DESTROY_LIST" : 3,
    "REMOVE_ENTRY" : 4,
    "LIST_LENGTH" : 5
}
"""
Dict for different broadcast functions.

- ADD_LIST : 1
- VIEW_LIST : 2
- DESTROY_LIST : 3
- REMOVE_ENTRY : 4
- LIST_LENGTH : 5
"""

def resetDevice():
    """
    Reset Device (0) (0 bytes)

    RP1210_RESET_DEVICE only works if only one client is connected to the adapter, and does
    the exact same thing as if you called the function ClientDisconnect.

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
    Set Message Filtering for CAN (5) (9 bytes)

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

def generic(ClientCommand, num_bytes = 0, byteorder = 'big') -> bytes:
    """
    Generic Driver Command (14)

    Args:
    - ClientCommand - the bytes/buffer to be sent to the drivers.
    - size = size of ClientCommand. Leave 0 to automatically size to len(ClientCommand).
    - byteorder = big endian ('big') or little endian ('little')
    """
    return sanitize_msg_param(ClientCommand, num_bytes, byteorder)

def setEcho(echo = True) -> bytes:
    """
    Set Echo Transmitted Messages (16) (1 byte)

    Args:
    - Echo on/off (bool) - False for no echo, True for echo.
    """
    if echo:
        msg = ECHO_MODES["ECHO_ON"]
    else:
        msg = ECHO_MODES["ECHO_OFF"]
    return sanitize_msg_param(msg, 1)

def setAllFiltersToDiscard():
    """
    Set All Filter States to Discard (17) (0 bytes)

    Returns empty byte string (this command needs no extra data).
    """
    return b''

def setMessageReceive(receive_messages = True) -> bytes:
    """
    Set Message Receive (18) (1 byte)

    Args:
    - Receive on/off : True = RECEIVE_ON, False = RECEIVE_OFF.
    """
    if receive_messages:
        msg = RECEIVE_MODES["RECEIVE_ON"]
    else:
        msg = RECEIVE_MODES["RECEIVE_OFF"]
    return sanitize_msg_param(msg, 1)

def protectJ1939Address(address_to_claim, network_mgt_name, blocking = True) -> bytes:
    """
    Protect J1939 Address (19) (10 bytes)

    This command claims an address on the J1939 bus.
    - address_to_claim (1 byte) - 8-bit address to claim on the J1939 bus.
    - network_mgt_name (8 bytes) - 8-byte name of client on network (this is you!)
        - See J1939 network management standard!
        - Lowest name takes priority if two devices try to claim the same address
    - blocking (bool) - True will block until done, False will return before completion
    """
    addr = sanitize_msg_param(address_to_claim, 1)
    name = sanitize_msg_param(network_mgt_name, 8)
    if blocking:
        status = sanitize_msg_param(0, 1) # BLOCK_UNTIL_DONE
    else:
        status = sanitize_msg_param(2, 1) # RETURN_BEFORE_COMPLETION
    return addr + name + status

def releaseJ1939Address(address) -> bytes:
    """
    Release a J1939 Address (31) (1 byte)

    Args:
    - Address (1 byte) - the address to release.

    This doesn't do anything special with the J1939 bus. All it does is tell your adapter not to
    use this address anymore.
    """
    return sanitize_msg_param(address, 1)
    

def setBroadcastList(function : Literal[1, 2, 3, 4, 5], command) -> bytes:
    """
    A catch-all function for each RP1210_Set_Broadcast_For_XXX command, since each one takes
    the same type of ClientCommand argument.

    Function codes:
    - 1 = ADD_LIST
    - 2 = VIEW_B_LIST
    - 3 = DESTROY_LIST
    - 4 = REMOVE_ENTRY
    - 5 = LIST_LENGTH

    Param command is equivalent to fpchClientCommand[1..n] input to RP1210_SendCommand.

    This function is mostly useful for building the following functions:
    - addBroadcastList
    - viewBroadcastList
    - destroyBroadcastList
    - removeBroadcastEntry
    - getBroadcastListLength

    This function applies for protocols J1708, CAN, J1939, J1850, ISO15765, ISO9141, and KWP2000.
    """
    func = sanitize_msg_param(function, 1)
    # if not func in [b'\x01', b'\x02', b'\x03', b'\x04', b'\x05']:
    #     raise ValueError("function must be one of:", "ADD_LIST (1)", "VIEW_B_LIST (2)", 
    #                         "DESTROY_LIST (3)", "REMOVE_ENTRY (4)", "LIST_LENGTH (5")
    ret_val = func
    ret_val += sanitize_msg_param(command)
    return ret_val


def setFilterType(filter_type : Literal[0, 1]):
    """
    Set Filter Type (1 byte)

    filter_type:
    - 0 = FILTER_INCLUSIVE
    - 1 = FILTER_EXCLUSIVE

    Used for:
    - RP1210_Set_J1708_Filter_Type (24)
    - RP1210_Set_J1939_Filter_Type (25)
    - RP1210_Set_CAN_Filter_Type (26)
    - RP1210_Set_J1850_Filter_Type (30)
    - RP1210_Set_IS015765_Filter_Type (32)
    """
    val = sanitize_msg_param(filter_type, 1)
    # if not val in [b'\x00', b'\x01']:
    #     raise ValueError("filter_type must be 0 (FILTER_INCLUSIVE) or 1 (FILTER_EXCLUSIVE)")
    return val

def setJ1939InterpacketTime(time_in_ms : int):
    """
    Set J1939 Broadcast Interpacket Timing (27)

    Args:
    - time_in_ms - interpacket time in milliseconds (unsigned 32-bit int)
    """
    return sanitize_msg_param(time_in_ms, 4, 'little')

def setMaxErrorMsgSize(msg_size : int):
    """
    Set Max Error Message Return Size (28)

    Args:
    - msg_size - value in bytes for how large error messages are allowed to be.
        - Should be between 81 and 65535
    """
    return sanitize_msg_param(msg_size, 2, 'little')

def disallowConnections():
    """
    Disallow Further Client Connections (29)

    There is no data required for this command, so this function will return b''
    """
    return b''

def setJ1939Baud(baud_code : int, wait_for_msg = True):
    """
    Set J1939 Baud Rate (37)

    Args:
    - baud_code - code that corresponds w/ desired baud rate
        - 125k = 4
        - 250k = 5
        - 500k = 6
        - 1000k = 7
    - wait_for_msg - should we apply the baud change after the current message is finished, or
                    apply the change right away?
    """
    # translate codes if applicable
    # TODO: Replace this with the translation functions below this function.
    if baud_code in [125000, 125, '125', '125k', '125000']:
        baud_code = 0x04
    elif baud_code in [250000, 250, '250', '250k', '250000']:
        baud_code = 0x05
    elif baud_code in [500000, 500, '500', '500k', '500000']:
        baud_code = 0x06
    elif baud_code in [1000000, 1000, '1000', '1000000', '1000k']:
        baud_code = 0x07
    # check wait_for_msg flag
    if wait_for_msg:
        wait_msg = b'\x01'
    else:
        wait_msg = b'\x00'
    # return value
    return wait_msg + sanitize_msg_param(baud_code, 1)

def setBlockingTimeout(block1 : int, block2 : int):
    """
    Set Blocking Timeout (215) (2 bytes)

    Block 1 and block 2 are multiplied together to determine the final blocking time in
    milliseconds. Set either block to 0 for infinite time.
    """
    return sanitize_msg_param(block1, 1) + sanitize_msg_param(block2, 1)

def flushBuffers():
    """
    Flush the Send/Receive Buffers (39)

    There is no data required for this command, so this function will return b''
    """
    return b''

def getConnectionSpeed():
    """
    What Speed Did the VDA Connect? (45)

    There is no data required for this command, so this function will return b''
    """
    return b''

def setCANBaud(baud_code : int, wait_for_msg = True):
    """
    Set CAN Baud Rate (47)

    Args:
    - baud_code - code that corresponds w/ desired baud rate
        - 9600 = 0
        - 19200 = 1
        - 38400 = 2
        - 57600 = 3
        - 125k = 4
        - 250k = 5
        - 500k = 6
        - 1000k = 7
    - wait_for_msg - should we apply the baud change after the current message is finished, or
                    apply the change right away?
    """
    # translate codes if applicable
    if baud_code in [9600, 9.6, '9600', '9.6k']:
        baud_code = 0x00
    elif baud_code in [19200, 19.2, '19200', '19.2k']:
        baud_code = 0x01
    elif baud_code in [38400, 38.4, '38400', '38.4k']:
        baud_code = 0x02
    elif baud_code in [57600, 57.6, '57600', '57.6k']:
        baud_code = 0x03
    elif baud_code in [125000, 125, '125', '125k', '125000']:
        baud_code = 0x04
    elif baud_code in [250000, 250, '250', '250k', '250000']:
        baud_code = 0x05
    elif baud_code in [500000, 500, '500', '500k', '500000']:
        baud_code = 0x06
    elif baud_code in [1000000, 1000, '1000', '1000000', '1000k']:
        baud_code = 0x07
    # check wait_for_msg flag
    if wait_for_msg:
        wait_msg = b'\x01'
    else:
        wait_msg = b'\x00'
    # return value
    return wait_msg + sanitize_msg_param(baud_code, 1)
