import RP1210

# Demo with RP1210Config
print('------------------- Device NULN2R32 --------------------')
config = RP1210.RP1210Config("NULN2R32")
for protocol in config.getProtocols():
    print(f"{protocol} --------")
    print(f"Description: {protocol.getDescription()}")
    print(f"Speed: {protocol.getSpeed()}")
    print(f"Params: {protocol.getParams()}")
    print(f"Protocol string: {protocol.getString()}")
    print(f"Devices: {protocol.getDevices()}")

# Demo with custom device
# define section directory for RP1210Protocol class
print('---------- Customized protocol configuration -----------')
section = {
    "ProtocolDescription": "Some protocol description",
    "ProtocolSpeed": "100,200,300",
    "ProtocolString": "Some protocol strings",
    "ProtocolParams": "Some protocol parameters",
    "Devices": "1,2,3"
}

# initialize protocol
protocol = RP1210.RP1210Protocol(section)
print(protocol)
print(f"Description: {protocol.getDescription()}")
print(f"Speed: {protocol.getSpeed()}")
print(f"Params: {protocol.getParams()}")
print(f"Protocol string: {protocol.getString()}")
print(f"Devices: {protocol.getDevices()}")
