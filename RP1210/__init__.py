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

from RP1210.RP1210C import RP1210_ERRORS, RP1210_COMMANDS, RP1210API, RP1210Config, RP1210Device, RP1210Protocol, getAPINames, translateErrorCode, sanitize_msg_param
