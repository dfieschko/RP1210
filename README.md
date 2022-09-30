# RP1210 for Python

```
pip install rp1210
```
A Python module for interacting with RP1210 adapter drivers, following the RP1210C standard.
Contributions welcome!

Some documentation and examples are available in [this repo's wiki](https://github.com/dfieschko/RP1210/wiki) and the Examples folder.

This module was written and tested with Python 3.9 and 3.10, 32-bit. Older (and newer) Python versions have not been tested and may not be supported.   
32-bit Python is required because RP1210 drivers are all 32-bit,
and can thus only be loaded with 32-bit Python. A 64-bit implementation via
[MSL-LoadLib](https://github.com/MSLNZ/msl-loadlib) is possible and may be released as a separate
module sometime in the future.

**This module is currently in alpha, and changes to core functionality may happen.** Once it hits beta,
I will start taking care not to break people's code. Until then, expect changes. You can keep track of planned changes in the [Issues](https://github.com/dfieschko/RP1210/issues) page.

Not all aspects of the RP1210C standard are fully implemented as independent features. Currently, my focus is on J1939 communication.
Other protocols have significantly less support, but you can still access all the low-level commands via the `RP1210API` class.

While I try to provide adequate documentation, the RP1210C standard is owned by TMC, not me, and is
not reproduced here. For a complete understanding of the RP1210 standard, you must purchase and
read the official RP1210C documentation from TMC.

Official RP1210C documentation can be purchased from TMC at this link ($37.50 at time of writing):
    https://www.atabusinesssolutions.com/Shopping/Product/viewproduct/2675472/TMC-Individual-RP

### Getting Started
```python
from RP1210 import RP1210Client, translateErrorCode

# init client
client = RP1210Client()

# select vendor and device
client.setVendor("NULN2R32") # Nexiq USB-Link 2 in this case
client.setDevice(1) # wired USB-Link 2

# connect to adapter w/ specified protocol
clientID = client.connect(b'J1939:Baud=Auto') # will return clientID or error code
error_msg = translateErrorCode(clientID)
if error_msg != "NO_ERRORS": # failed to connect
   print("Connection failed:", error_msg)

# read all messages (no filter)
client.setAllFiltersToPass()

# send a message
msg = b'message contents'
err_code = client.tx(msg)
print("Tx Result:", translateErrorCode(err_code))

# read messages
while True:
   msg = client.rx()
   if msg: # message was received
      print(msg)
```
