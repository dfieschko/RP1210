import RP1210

# get available names from C:\Windows\RP121032.ini
API_NAMES = RP1210.getAPINames()

print("Available API names:", API_NAMES)

# Replace this with desired driver name (must be in API_NAMES)
API_NAME = "NULN2R32"

DEVICE_ID = 1  # Get this from driver .ini file, e.g. C:\Windows\NULN2R32.ini

if API_NAME not in API_NAMES:
    print("You don't have the right drivers installed!")

# initialize the API
api = RP1210.RP1210API(API_NAME)

# check if the connected adapter confirms to the RP1210C standard
print("The connected adapter confirms to the RP1210C standard: ",
      api.conformsToRP1210C())

# attempt to connect to the adapter
clientID = api.ClientConnect(DEVICE_ID)  # Try to connect w/ default settings

# check if connection succeeded
if clientID in range(1, 128):
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
    print("Hardware status is: ", hardwareStatus)

    # now we need to set the adapter's filters to allow messages through
    # SET_ALL_FILTERS_STATES_TO_PASS has command ID 3 (see Commands.py)
    print('-------------- Reading message start ----------------')
    cmd_code_arr = [3, 9, 305]
    for code in cmd_code_arr:
        cmdCode = api.SendCommand(code, clientID)
        print(f"Command received: {cmdCode}")
        for _ in range(1, 10000):
            msg = api.ReadDirect(clientID)
            if msg:
                print("Received message:", api.ReadMessage(clientID, msg))
            # else:
            #     print('No Message received')
    print('-------------- Reading message end ----------------')

    print('-------------- Sending message start ----------------')
    # send message to adapter
    send_msg_arr = [b'\xff\xff\xff\xff\x8f\xff\xff\xff',
                    b'\x00\x00\xbe\xef\xca\xfe',
                    b'\x01\x00\xbe\x8f\xca\xfe',
                    b'`',
                    b'\x00']

    for sendmsg in send_msg_arr:
        sendmsg_code = api.SendMessage(clientID, sendmsg)
        if sendmsg_code == 0:
            print("Success. Message: ", sendmsg,
                  ", Message sending status: ", sendmsg_code)
        else:
            print("Failure. Message: ", sendmsg, ", Message sending status: ",
                  sendmsg_code, ", Error message: ", RP1210.translateErrorCode(sendmsg_code))
    print('-------------- Sending message end ----------------')
else:
    print(
        f"Failed to connect. Error code: {clientID}, error message: {api.GetErrorMsg(clientID)}")

# disconnect the adapter
api.ClientDisconnect(DEVICE_ID)
print("Adapters disconnected.")
