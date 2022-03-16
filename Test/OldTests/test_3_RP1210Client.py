from ctypes import create_string_buffer
from RP1210 import RP1210Client, J1939
import pytest
from tkinter import messagebox
import time

from RP1210.RP1210 import RP1210API

TEST_ENABLED = False
SKIP_REASON = "Dual adapter tests are disabled."

if not TEST_ENABLED:
    pytest.skip(SKIP_REASON, allow_module_level=True)

def test_dual_adapters_begin():
    messagebox.showinfo("Connect your dual adapter setup!", 
                        "Connect your Noregon DLA2 and Nexiq USB-Link 2 together and power them up!")


def test_dual_clients_tx_rx():
    nexiq = RP1210Client()
    dla2 = RP1210Client()
    # set vendors and devices
    nexiq.setVendor("NULN2R32")
    nexiq.setDevice(1)
    dla2.setVendor("DLAUSB32")
    dla2.setDevice(100)
    # connect to adapter
    err_code = nexiq.connect(b"J1939:Baud=500")
    assert 0 <= err_code <= 127
    time.sleep(0.01)
    err_code = dla2.connect(b"J1939:Baud=500")
    assert 0 <= err_code <= 127
    time.sleep(0.01)
    # set all filters to pass
    err_code = nexiq.setAllFiltersToPass()
    assert 0 <= err_code <= 127
    time.sleep(0.01)
    err_code = dla2.setAllFiltersToPass()
    assert 0 <= err_code <= 127

    # send J1939 message
    msg = J1939.toJ1939Message(0xFEDA, 6, 0x4E, 0xFF, 0xC0FFEE)
    start_time = time.time()
    assert nexiq.tx(msg) == 0
    # receive J1939 message
    msg_received = b''
    while time.time() - start_time < 1 and msg_received == b'':
        assert nexiq.tx(msg) == 0
        time.sleep(0.001)
        msg_received = dla2.rx()
        time.sleep(0.001)
    # disconnect adapters before asserts so as not to fill up client pool
    assert nexiq.disconnect() == 0
    assert dla2.disconnect() == 0
    # check that msg was received and matches message that was sent
    assert msg_received != b''
    assert msg_received[4:] == msg

