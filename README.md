# RP1210 for Python

```
pip install rp1210
```
A Python module for interacting with RP1210 adapter drivers, following the RP1210C standard.
Contributions welcome!

Documentation and examples are in [this repo's wiki](https://github.com/dfieschko/RP1210/wiki).

This module was written and tested with Python 3.9, 32-bit. Older Python versions have not been
tested and may not be supported. 32-bit Python is required because RP1210 drivers are all 32-bit,
and can thus only be loaded with 32-bit Python. A 64-bit implementation via
[MSL-LoadLib](https://github.com/MSLNZ/msl-loadlib) is planned and may be released as a separate
module.

**This module is currently in alpha, and changes to core functionality may happen.** Once it hits beta,
I will start taking care not to break people's code. Until then, expect changes. I will consider the
project to be in beta when I have representation for all RP1210 Commands, most RP1210 protocols, and
an RP1210Client class that handles the nitty gritty of connecting to and communicating with an adapter.

Not all aspects of the RP1210C standard are implemented. Currently, my focus is on J1939 communication.
Other protocols have significantly less support.

While I try to provide adequate documentation, the RP1210C standard is owned by TMC, not me, and is
not reproduced here. For a complete understanding of the RP1210 standard, you must purchase and
read the official RP1210C documentation from TMC.

Official RP1210C documentation can be purchased from TMC at this link ($37.50 at time of writing):
    https://www.atabusinesssolutions.com/Shopping/Product/viewproduct/2675472/TMC-Individual-RP

## Examples

```python
# importing modules
from RP1210 import RP1210, J1939, Commands
```

```python
# get available API names
api_names = RP1210.getAPINames()
```

```python
# load information from an RP1210 config file
nexiq_api_name = "NULN2R32" # or use values from RP1210.getAPINames()
# load from config file
nexiq = RP1210.RP1210Config(nexiq_api_name)
# read properties
nexiq_description = nexiq.getDescription()
nexiq_device_ids = nexiq.getDevices()
# access an API through RP1210Config
clientID = nexiq.api.ClientConnect(nexiq_device_ids[0], b"J1939:Baud=500")
...
```

```python
# access an API directly (without RP1210Config)
api_names = RP1210.getAPINames()
api_name = api_names[0]
api = RP1210.RP1210API(api_name)
clientID = api.ClientConnect(...)
...
```

```python
# using RP1210C.Commands to help w/ claiming a J1939 address
... # assume api has been initalized and ClientConnect has been called
my_address = 42
my_network_mgt_name = 0xDEADBEEF

# generate params
cmd_num = Commands.COMMAND_IDS["PROTECT_J1939_ADDRESS"] # == 19
cmd_data = Commands.protectJ1939Address(my_address, my_network_mgt_name)
# call SendCommand
err_code = nexiq.api.SendCommand(cmd_num, clientID, cmd_data)
```
