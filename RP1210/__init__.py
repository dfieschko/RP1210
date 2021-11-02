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

def sanitize_msg_param(param, num_bytes : int = 0, byteorder : str = 'big') -> bytes:
    """
    'Sanitizes' (converts to bytes) a message parameter.

    Defaults to big-endianness and whatever the size of param is.

    This function is meant for internal use in message/protocol files; it's only public because
    I didn't want to copy/paste it a bunch of times.
    """
    if isinstance(param, str): # string to bytes
        if param == "": # check for empty string
            return b'' + b'\x00' * num_bytes
        return sanitize_msg_param(int(param), num_bytes, byteorder)
    if isinstance(param, int): # int to bytes
        if num_bytes == 0:
            num_bytes = (param.bit_length() + 7) // 8
            if param == 0: # don't cut it off if the input is zero
                num_bytes = 1
        return param.to_bytes(num_bytes, byteorder)
    if isinstance(param, bytes):
        try:    # decode from UTF-8
            return sanitize_msg_param(int(param.decode('utf8')), num_bytes, byteorder)
        except ValueError: # not in utf8 format
            # check if we need to add padding
            if len(param) < num_bytes:
                padding = b'\x00' * (num_bytes - len(param))
            else:
                padding = b''
            # add padding before or after, depending on endianness
            if byteorder == 'big':
                return padding + param
            else:
                return param + padding
    
