# RP1210 for Python

```
pip install rp1210
```
A Python module for interacting with RP1210 adapter drivers, following the RP1210C standard.
Contributions welcome!

Documentation and examples will be in [this repo's wiki](https://github.com/dfieschko/RP1210/wiki) once I actually get around to writing them.

This module was written and tested with Python 3.9 and 3.10, 32-bit. Older (and newer) Python versions have not been tested and may not be supported.   
32-bit Python is required because RP1210 drivers are all 32-bit,
and can thus only be loaded with 32-bit Python. A 64-bit implementation via
[MSL-LoadLib](https://github.com/MSLNZ/msl-loadlib) is planned and may be released as a separate
module sometime in the future.

**This module is currently in alpha, and changes to core functionality may happen.** Once it hits beta,
I will start taking care not to break people's code. Until then, expect changes. You can keep track of planned changes in the [Issues](https://github.com/dfieschko/RP1210/issues) page.

Not all aspects of the RP1210C standard are implemented. Currently, my focus is on J1939 communication.
Other protocols have significantly less support.

While I try to provide adequate documentation, the RP1210C standard is owned by TMC, not me, and is
not reproduced here. For a complete understanding of the RP1210 standard, you must purchase and
read the official RP1210C documentation from TMC.

Official RP1210C documentation can be purchased from TMC at this link ($37.50 at time of writing):
    https://www.atabusinesssolutions.com/Shopping/Product/viewproduct/2675472/TMC-Individual-RP
