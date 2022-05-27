import RP1210

# Demo with RP1210Config
print('--------------------- Device NULN2R32 ----------------------')
config = RP1210.RP1210Config("NULN2R32")

for device in config.getDevices():
    print(device)
    print(f"Device ID: {device.getID()}")
    print(f"Device Description: {device.getDescription()}")
    print(f"Device Name: {device.getName()}")
    print(f"Device Params: {device.getParams()}")
    print(f"MultiCANChannels: {device.getMultiCANChannels()}")
    print(f"MultiJ1939Channels: {device.getMultiJ1939Channels()}")

# Demo with custom device
# define section dictionary for RP1210Device
print('------------- Customized device configuration --------------')
section = {
    "DeviceID": "111",
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
