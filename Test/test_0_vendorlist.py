from configparser import ConfigParser
import os
import pytest
from RP1210 import sanitize_msg_param
import RP1210
from ctypes import cdll, create_string_buffer
from RP1210.RP1210 import RP1210VendorList, getAPINames

API_NAMES = ["PEAKRP32", "DLAUSB32", "DGDPA5MA", "NULN2R32", "CMNSI632", "CIL7R32", "DrewLinQ", "DTKRP32"]
INVALID_API_NAMES = ["empty_api", "invalid_api", "extra_empty_api", "invalid_pd_api"]

# These tests are meant to be run with cwd @ repository's highest-level directory
CWD = os.getcwd()
TEST_FILES_DIRECTORY = CWD + ".\\Test\\test-files"
INI_DIRECTORY = TEST_FILES_DIRECTORY + "\\ini-files"
DLL_DIRECTORY = TEST_FILES_DIRECTORY + "\\dlls"
RP121032_PATH = TEST_FILES_DIRECTORY + "\\RP121032.ini"

# try to get Windows Server to load DLLs w/ GitHub Actions
os.add_dll_directory(DLL_DIRECTORY)
os.add_dll_directory(os.getcwd())
os.environ['PATH'] += os.pathsep + DLL_DIRECTORY
for d in os.environ['path'].split(';'): # overboard
    if os.path.isdir(d):
        os.add_dll_directory(d)

invalid_apis = [] + INVALID_API_NAMES

# Check which APIs are missing dependencies so they can be skipped
for api_name in API_NAMES:
    valid = True
    try:
        ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
        dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
        rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
        if api_name not in invalid_apis:
            valid = rp1210.getAPI().isValid()
    except Exception:
        valid = False
    if not valid:
        invalid_apis.append(api_name)

def test_cwd():
    """Make sure cwd isn't in Test folder."""
    cwd = os.getcwd()
    assert "RP1210" in cwd
    assert "Test" not in cwd

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_api_files_exist(api_name : str):
    """Makes sure all the relevant API files are in test-files directory."""
    assert os.path.exists(TEST_FILES_DIRECTORY)
    assert os.path.exists(INI_DIRECTORY)
    assert os.path.exists(DLL_DIRECTORY)
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    assert os.path.isfile(ini_path)
    assert os.path.isfile(RP121032_PATH)
    if not api_name in invalid_apis:
        assert os.path.isfile(dll_path)
        assert cdll.LoadLibrary(dll_path) != None

def test_vendorlist_init():
    """
    Initializes VendorList just to see if the program crashes, but doesn't do much else.
    Doesn't require any adapter software to be installed.
    """
    vendors = RP1210.RP1210VendorList()
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors
    vendor_names = []
    for vendor in vendors:
        vendor_names.append(vendor.getAPIName())
    for name in API_NAMES:
        if name not in invalid_apis:
            assert name in vendor_names


def test_vendorlist_rp1210config_objects():
    """
    Makes sure that all RP1210Config objects that are possible to read from
    RP121032.ini are present in RP1210VendorList.
    """
    vendor_names = getAPINames(RP121032_PATH)
    assert vendor_names
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors
    for vendor in vendors.getList():
        assert vendor.getAPIName() in vendor_names or vendor.getAPIName() in invalid_apis

def test_vendorlist_index():
    """
    Iterates through a bunch of indices for vendors and devices to make sure an invalid index
    doesn't cause a crash.
    """
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
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
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.getList() != []
    assert vendors.getList() == vendors.getVendorList()

def test_numvendors():
    """
    Test getList() function. Must have at least one adapter driver installed to pass
    this test.
    """
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.numVendors() != 0
    assert vendors.numVendors() == len(vendors.getList())

def test_vendors_and_devices():
    """
    Run through each vendor and device and make sure everything matches.
    """
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
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
