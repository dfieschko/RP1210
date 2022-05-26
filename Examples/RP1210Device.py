import RP1210

# define section dictionary for RP1210Device
section = {
    "DeviceID": "1",
    "DeviceDescription": "Some device description",
    "DeviceName": "xyz",
    "DeviceParams": "Some device parameters",
    "MultiCANChannels": "1",
    "MultiJ1939Channels": "1"
}

# intialize device
device = RP1210.RP1210Device(section)

# print device information
print(device)
print(f"Device ID: {device.getID()}")
print(f"Device Description: {device.getDescription()}")
print(f"Device Name: {device.getName()}")
print(f"Device Params: {device.getParams()}")
print(f"MultiCANChannels: {device.getMultiCANChannels()}")
print(f"MultiJ1939Channels: {device.getMultiJ1939Channels()}")
