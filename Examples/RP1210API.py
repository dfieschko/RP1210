import RP1210

# get available names from C:\Windows\RP121032.ini
API_NAMES = RP1210.getAPINames()

print("Available API names:", API_NAMES)

# Replace this with desired driver name (must be in API_NAMES)
API_NAME = "NULN2R32"

DEVICE_ID = 1  # Get this from driver .ini file, e.g. C:\Windows\NULN2R32.ini

# See example for RP1210Config for more info on how to select API name and Device ID.

if API_NAME not in API_NAMES:
    print("You don't have the right drivers installed!")

# initialize the API
api = RP1210.RP1210API(API_NAME)

# check if the connected adapter conforms to the RP1210C standard
print("The connected adapter conforms to the RP1210C standard: ",
      api.conformsToRP1210C())

# attempt to connect to the adapter
clientID = api.ClientConnect(DEVICE_ID)  # Try to connect w/ default settings

if clientID in range(128):  # if connection succeeded
    print(
        f"Successfully connected and received code: {clientID} ({RP1210.translateErrorCode(clientID)})\n")

    # call ReadVersionDirect and print DLL and API version
    versionInfo = api.ReadVersionDirect()
    print(f"ReadVersionDirect DLL Version: {versionInfo[0]}")
    print(f"ReadVersionDirect API Version: {versionInfo[1]}")

    # call ReadDetailedVersionDirect and print DLL, API, FW
    detailedVerInfo = api.ReadDetailedVersionDirect(clientID)
    print(f"ReadDetailedVersionDirect DLL Version: {detailedVerInfo[0]}")
    print(f"ReadDetailedVersionDirect API Version: {detailedVerInfo[1]}")
    print(f"ReadDetailedVersionDirect FW Version: {detailedVerInfo[2]}")

    # call GetHardwareStatusDirect and print
    hardwareStatus = api.GetHardwareStatusDirect(clientID)
    print("Hardware status bytes translate to: ", hardwareStatus)

    print('-------------- Reading message start ----------------')

    # now we need to set the adapter's filters to allow messages through
    # we will also send another two arbitrary commands to the adapter.
    # SET_ALL_FILTERS_STATES_TO_PASS has command ID 3 (see Commands.py)
    cmd_code_arr = [3, 9, 305]
    for code in cmd_code_arr:
        # We call SendCommand to send a command to the adapter
        cmdCode = api.SendCommand(code, clientID)
        print(
            f"Command sent. Return code: {cmdCode} ({RP1210.translateErrorCode(cmdCode)})")
        for _ in range(1, 10000):
            # We call ReadDirect, which sets up and calls RP1210_ReadMessage for us.
            msg = api.ReadDirect(clientID)
            if msg:
                print("Received message:", msg)
            # else:
            #     print('No Message received')
    print('-------------- Reading message end ----------------')

    # Now let's send some messages!
    print('-------------- Sending message start ----------------')
    # send message to adapter
    send_msg_arr = [b'\xff\xff\xff\xff\x8f\xff\xff\xff',
                    b'\x00\x00\xbe\xef\xca\xfe',
                    b'\x01\x00\xbe\x8f\xca\xfe',
                    b'`',
                    b'\x00']

    for sendmsg in send_msg_arr:
        # We call SendMessage, which sends bytes to the adapter to transmit on the databus.
        sendmsg_code = api.SendMessage(clientID, sendmsg)
        if sendmsg_code == 0:
            print("Success. Message: ", sendmsg,
                  ", Message sending status: ", sendmsg_code)
        else:
            print("Failure. Message: ", sendmsg, ", Message sending status: ",
                  sendmsg_code, ", Error message: ", RP1210.translateErrorCode(sendmsg_code))
    print('-------------- Sending message end ----------------')

    # disconnect the adapter by calling RP1210_ClientDisconnect
    disconnectCode = api.ClientDisconnect(clientID)
    if disconnectCode == 0:
        print("Adapters disconnected successfully.")
    else:
        print("Adapter failed to disconnect:",
              RP1210.translateErrorCode(disconnectCode))
else:
    # Connection failed. Call RP1210_GetErrorMsg to print the error message.
    print(
        f"Failed to connect. Error code: {clientID}, error message: {api.GetErrorMsg(clientID)}")
