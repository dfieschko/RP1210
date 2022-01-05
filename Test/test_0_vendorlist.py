from configparser import ConfigParser
import os
from RP1210 import sanitize_msg_param
import RP1210
from RP1210.RP1210 import getAPINames

def test_vendorlist_init():
    """
    Initializes VendorList, but doesn't do much else.
    Doesn't require any adapter software to be installed.
    """
    vendors = RP1210.RP1210VendorList()

def test_vendorlist_rp1210config_objects():
    """
    Makes sure that all RP1210Config objects that are possible to read from
    RP121032.ini are present in RP1210VendorList.
    """
    vendor_names = getAPINames()
    assert vendor_names
    vendors = RP1210.RP1210VendorList()
    assert vendors
    for vendor in vendors.getList():
        assert vendor.getAPIName() in vendor_names

