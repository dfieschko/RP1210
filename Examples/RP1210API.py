import RP1210

API_NAMES = RP1210.getAPINames() # get available names from C:\Windows\RP121032.ini

print("Available API names:", API_NAMES)

API_NAME = "NULN2R32" # Replace this with desired driver name (must be in API_NAMES)

DEVICE_ID = 1 # Get this from driver .ini file, e.g. C:\Windows\NULN2R32.ini

if API_NAME not in API_NAMES:
    print("You don't have the right drivers installed!")

# initialize the API
api = RP1210.RP1210API(API_NAME)

# attempt to connect to the adapter
clientID = api.ClientConnect(DEVICE_ID) # Try to connect w/ default settings
print(f"Attempted connection and received code: {clientID} ({RP1210.translateErrorCode(clientID)})")

# call ReadVersionDirect and print DLL and API version
versionInfo = api.ReadVersionDirect()
print(f"DLL Version: {versionInfo[0]}")
print(f"API Version: {versionInfo[1]}")

# now we need to set the adapter's filters to allow messages through
# SET_ALL_FILTERS_STATES_TO_PASS has command ID 3 (see Commands.py)
cmdCode = api.SendCommand(3, clientID)

if RP1210.translateErrorCode(clientID) == "NO_ERRORS":
    while True:
        msg = api.ReadDirect(clientID) # read messages on J1939 bus
        if msg:
            print("Received message:", msg)
else:
    print("Connection was unsuccessful :(")