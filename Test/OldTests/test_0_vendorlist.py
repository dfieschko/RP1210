from configparser import ConfigParser
import os
from RP1210 import sanitize_msg_param
import RP1210
from RP1210.RP1210 import RP1210VendorList, getAPINames

def test_vendorlist_init():
    """
    Initializes VendorList just to see if the program crashes, but doesn't do much else.
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

def test_vendorlist_index():
    """
    Iterates through a bunch of indices for vendors and devices to make sure an invalid index
    doesn't cause a crash.
    """
    vendors = RP1210.RP1210VendorList()
    for x in range(-10, 50):
        vendors.setVendorIndex(x)
        vendors.getVendor(x)
        vendors.getCurrentVendor()
        for y in range(-10, 1000):
            vendors.setDeviceIndex(y)
            vendors.getCurrentDevice()
        vendors.getAPI()

def test_getlist():
    """
    Test getList() function. Must have at least one adapter driver installed to pass
    this test.
    """
    vendors = RP1210VendorList()
    assert vendors.getList() != []
    assert vendors.getList() == vendors.getVendorList()

def test_numvendors():
    """
    Test getList() function. Must have at least one adapter driver installed to pass
    this test.
    """
    vendors = RP1210VendorList()
    assert vendors.numVendors() != 0
    assert vendors.numVendors() == len(vendors.getList())

def test_vendors_and_devices():
    """
    Run through each vendor and device and make sure everything matches.
    """
    vendors = RP1210VendorList()
    # check vendors
    for vendorIndex in range(vendors.numVendors()):
        vendors.setVendorIndex(vendorIndex)
        assert vendors.deviceIndex == 0 # setting vendor index should set device index to 0
        # check devices
        for deviceIndex in range(vendors.numDevices()):
            # check that setting by device name goes to correct index
            vendors.setDeviceIndex(deviceIndex)
            deviceID = vendors.getCurrentDevice().getID()
            vendors.setDevice(deviceID)
            assert vendors.deviceIndex == deviceIndex
            assert vendors.getCurrentDevice().getID() == deviceID
        # check that setting by api name goes to correct index
        api_name = vendors.getCurrentVendor().getAPIName()
        vendors.setVendor(api_name)
        # CMNSIM32 can sometimes be installed twice on a system
        assert vendors.vendorIndex == vendorIndex or api_name == "CMNSIM32"
