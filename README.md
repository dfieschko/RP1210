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
