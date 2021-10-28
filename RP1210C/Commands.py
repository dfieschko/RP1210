"""
Generate ClientCommand inputs for RP1210_SendCommand.

Each function in this file returns a value that can be used for ClientCommand.
"""
from RP1210C import sanitize_msg_param

def reset():
    """
    Reset Device (0)
    """
    return b''

def setAllFiltersToPass():
    """
    Set All Filter States to Pass (3)
    """
    return b''

def setJ1939Filters():
    """
    Set Message Filtering for J1939 (4)
    """
    #TODO

def setCANFilters():
    """
    Set Message Filtering for CAN (5)
    """
    #TODO

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
