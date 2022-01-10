"""
Module for interacting with RP1210 adapter drivers, following the RP1210C standard.
Contributions welcome!

Author: Darius Fieschko

While I try to provide adequate documentation, the RP1210C standard is owned by TMC, not me, and is
not reproduced here. For a complete understanding of the RP1210 standard, you must purchase and
read the official RP1210C documentation from TMC.

Official RP1210C documentation can be purchased from TMC at this link ($37.50 at time of writing):
    https://www.atabusinesssolutions.com/Shopping/Product/viewproduct/2675472/TMC-Individual-RP
"""
# Import everything from RP1210.py
from RP1210.RP1210 import *
from RP1210.functions import *
# Import other modules (not necessary in 3.9)
from RP1210 import Commands, J1939

