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
# Modules
from RP1210 import RP1210C, Commands, J1939
# RP1210C
from RP1210C import RP1210_ERRORS, RP1210_COMMANDS
from RP1210C import RP1210API, RP1210Config, RP1210Device, RP1210Protocol
from RP1210C import getAPINames, translateErrorCode, sanitize_msg_param
# J1939
from J1939 import J1939API, J1939MessageParser
from J1939 import toJ1939Message, toJ1939Request, getJ1939ProtocolString, getJ1939ProtocolDescription
