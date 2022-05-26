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


config = RP1210.RP1210Config(api_name=API_NAME)

# connect to the NEGIX adapter
api = config.api
clientID = api.ClientConnect(DEVICE_ID)

if clientID in range(128):  # if connection succeeded
    print(
        f"Successfully connected and received code: {clientID} ({RP1210.translateErrorCode(clientID)})\n")
    cmdCode = api.SendCommand(3, clientID)
    print(f"Command sent. Return code: {cmdCode} ({RP1210.translateErrorCode(cmdCode)})")
    for _ in range(1, 10000):
        if msg := api.ReadDirect(clientID):
            print("Received message:", msg)
        # else:
        #     print('No Message received')
else:
    # Connection failed. Call RP1210_GetErrorMsg to print the error message.
    print(
        f"Failed to connect. Error code: {clientID}, error message: {api.GetErrorMsg(clientID)}\n")

print("API info:", config)
print("The API is valid:", config.isValid())
print(f"Address: {config.getAddress1()}{config.getAddress2()}, {config.getCity()}, {config.getState()}, {config.getCountry()} {config.getPostal()}")
print(f"Telephone: {config.getTelephone()} | Fax: {config.getFax()}")
print(f"Vendor URL: {config.getVendorURL()}")
print(f"Version: {config.getVersion()}")
print(f"Auto Detect Capable: {config.autoDetectCapable()}")
print(f"Timestamp weight: {config.getTimeStampWeight()}")
print(f"Message: {config.getMessageString()}")
print(f"Error: {config.getErrorString()}")
print(f"RP1210 Version: {config.getRP1210Version()}")
print(f"Debug level: {config.getDebugLevel()}")
print(
    f"Debug file: {config.getDebugFile()}, file size: {config.getDebugFileSize()}")
print(f"Debug mode: {config.getDebugMode()}")
print(f"Number of sessions: {config.getNumberOfSessions()}")
print(f"CAN formats supported: {config.getCANFormatsSupported()}")
print(f"J1939 formats supported: {config.getJ1939FormatsSupported()}")
print(f"CAN auto baud: {config.getCANAutoBaud()}")
print(f"Connected device name: {config.getDevice(DEVICE_ID)}")
print("List of devices on the file:")
for device in config.getDevices():
    print(f"\t{device}")
print(f"List of device IDs on the file: {config.getDeviceIDs()}")
print(f"Current protocol: {config.getProtocol()}")
print("List of protocols on the file:")
for protocol in config.getProtocols():
    print(f"\t{protocol}")
print("List of protocol names:")
for protocol_name in config.getProtocolNames():
    print(f"\t{protocol_name}")
print(f"List of protocol IDs: {config.getProtocolIDs()}")


