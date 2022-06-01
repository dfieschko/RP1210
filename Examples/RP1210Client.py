from platform import release
import RP1210

# initialize RP1210Client and set vendor to DGDPA5MA
client = RP1210.RP1210Client()
client.setVendor("NULN2R32")

# connect to adapter
clientID = client.connect()
print("Client ID: ", clientID, "\n\tTranslate:",
      RP1210.translateErrorCode(clientID))

# send a command to the adapter
command = client.command(3)
print("Command sent. Return code:", command,
      "\n\tTranslate:", RP1210.translateErrorCode(command))

# read message
read_msg = client.rx()
print("Read message:", read_msg)

# send message to the adapter
send_msg = client.tx(b'\xff\xff\xff\xff\x8f\xff\xff\xff')
print("Message sent. Return code:", send_msg,
      "\n\tTranslate:", RP1210.translateErrorCode(send_msg))

# reset device
reset = client.resetDevice()
print("Reset device. Return code:", reset,
      '\n\tTranslate:', RP1210.translateErrorCode(reset))

# call function to set all filters to pass
print("All filters pass. Return code:", client.setAllFiltersToPass(),
      "\n\tTranslate:", RP1210.translateErrorCode(client.setAllFiltersToPass()))

# set message filtering for J1939
print("Set message fileting for J1939. Return code:", client.setJ1939Filters(
    0), "\n\tTranslate:", RP1210.translateErrorCode(client.setJ1939Filters(0)))

# # set message filtering for EXTENDED_CAN
# can_msg_filter = client.setCANFilters(0x01, 0xFFFFFFFF, 0xFFFFFFFF)  # ?
# print("Set message filtering for EXTENDED_CAN. Return code:",
#       can_msg_filter, "\n\tTranslate:", RP1210.translateErrorCode(can_msg_filter))

# set echo transmitted messages
print("Set echo transmitted messages. Return code:", client.setEcho(),
      "\n\tTranslate:", RP1210.translateErrorCode(client.setEcho()))

# set all filter states to discard
print("Set all filter states to discard. Return code:",
      client.setAllFiltersToDiscard(), "\n\tTranslate:", RP1210.translateErrorCode(client.setAllFiltersToDiscard()))

# set message receive to True
print("Set message receive to True. Return code:", client.setMessageReceive(),
      "\n\tTranslate:", RP1210.translateErrorCode(client.setMessageReceive()))

# # protect J1939 address
# reserve_address = client.protectJ1939Address(0xF9, 0)  # ?
# print("Protect J1939 address. Return code:", reserve_address,
#       "\n\tTranslate:", RP1210.translateErrorCode(reserve_address))

# # release a J1939 address
# release_address = client.releaseJ1939Address(0xF9)
# print("Release a J1939 address. Return code:", release_address,
#       "\n\tTranslate:", RP1210.translateErrorCode(release_address))

# set J1939 filter type to FILTER_INCLUSIVE
J1939_filter_type = client.setJ1939FilterType(0)
print("Set J1939 filter type to FILTER_INCLUSIVE. Return code:",
      J1939_filter_type, "\n\tTranslate:", RP1210.translateErrorCode(J1939_filter_type))

# set CAN filter type to FILTER_INCLUSIVE
can_filter_type = client.setCANFilterType(0)
print("Set CAN filter type to FILTER_INCLUSIVE. Return code:",
      can_filter_type, "\n\tTranslate:", RP1210.translateErrorCode(can_filter_type))

# set J1939 broadcast interpacket timing
J1939_broadcast_timing = client.setJ1939InterpacketTime(10)
print("Set J1939 broadcast interpacket timeing to 10ms. Return code:",
      J1939_broadcast_timing, "\n\tTranslate:", RP1210.translateErrorCode(J1939_broadcast_timing))

# set max error message size to 250
max_err_msg_size = client.setMaxErrorMsgSize(250)
print("Set max error message size to 250. Return code:", max_err_msg_size,
      "\n\tTranslate:", RP1210.translateErrorCode(max_err_msg_size))

# # disallow further client connections
# disallow_conn = client.disallowConnections()  # ? can't find a way to re-allow further
# print("Disallow further client connections. Return code:", disallow_conn,
#       "\n\tTranslate:", RP1210.translateErrorCode(disallow_conn))
# client1 = client.connect()
# print("Test if further connections are succeeded:", client1,
#       "\n\tTranslate:", RP1210.translateErrorCode(client1))

# set J1939 baud rate to 250k
print("Set J1939 baud rate to 250k. Return code:", client.setJ1939Baud(5),
      "\n\tTranslate:", RP1210.translateErrorCode(client.setJ1939Baud(5)))

# set blocking timeout to infinite time
block_timeout = client.setBlockingTimeout(0, 0)  # ?
print("Set blocking timeout to infinite time. Return code:", block_timeout,
      "\n\tTranslate:", RP1210.translateErrorCode(block_timeout))

# flush the send/receive buffer
flush_buffer = client.flushBuffers()
print("Flush the send/receive buffer. Return code:", flush_buffer,
      "\n\tTranslate:", RP1210.translateErrorCode(flush_buffer))

# get baud value
print("Baud value:", client.getBaud())

# set CAN baud rate to 57600
can_baud = client.setCANBaud(3)
print("Set CAN baud rate to 57600. Return code:", can_baud,
      "\n\tTranslate:", RP1210.translateErrorCode(can_baud))

# disconnect from adapter
disconnect_client = client.disconnect()
print("Disconnect:", disconnect_client, "\n\tTranslate:",
      RP1210.translateErrorCode(disconnect_client))
