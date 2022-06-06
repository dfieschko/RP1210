import os
import pytest
import RP1210
from ctypes import cdll
from RP1210.RP1210 import RP1210VendorList, getAPINames

API_NAMES = ["PEAKRP32", "DLAUSB32", "DGDPA5MA", "NULN2R32",
             "CMNSI632", "CIL7R32", "DrewLinQ", "DTKRP32"]
INVALID_API_NAMES = ["empty_api", "invalid_api",
                     "extra_empty_api", "invalid_pd_api"]

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
for d in os.environ['path'].split(';'):  # overboard
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
def test_api_files_exist(api_name: str):
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
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors
    assert len(vendors) == vendors.numVendors()
    vendor_names = []
    for vendor in vendors:
        vendor_names.append(vendor.getAPIName())
    for name in API_NAMES:
        if name not in invalid_apis:
            assert name in vendor_names


def test_vendorlist_nonevendors():
    """Force an error with vendor list and check numVendors()"""
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors
    assert vendors.numVendors()
    vendors.vendors = []
    assert not vendors
    assert not vendors.numVendors()
    vendors.vendors = None
    assert not vendors
    assert vendors.numVendors() == 0
    assert vendors.numDevices() == 0
    assert vendors.getAPI() is None
    assert vendors.getDeviceIndex(23) == 0
    assert vendors.getVendor() is None
    assert vendors.getVendorIndex("dinglebop") == 0
    assert vendors.getCurrentVendor() is None
    assert vendors.getVendorName() == ""
    assert vendors.getCurrentDevice() is None
    assert vendors.getDeviceID() == -1


def test_vendorlist_rp1210config_objects():
    """
    Makes sure that all RP1210Config objects that are possible to read from
    RP121032.ini are present in RP1210VendorList.
    """
    vendor_names = getAPINames(RP121032_PATH)
    assert vendor_names
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors
    for vendor in vendors.getList():
        assert vendor.getAPIName() in vendor_names or vendor.getAPIName() in invalid_apis


def test_vendorlist_index():
    """
    Iterates through a bunch of indices for vendors and devices to make sure an invalid index
    doesn't cause a crash.
    """
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.getVendorIndex("dinglebop") == 0
    assert vendors.getVendor("dinglebop") == vendors.getVendor(0)
    assert vendors.getDeviceIndex(23) == 0
    for x in range(-10, 50):
        vendors.setVendorIndex(x)
        vendors.getVendor(x)
        vendors.getCurrentVendor()
        for y in range(-10, 1000):
            vendors.setDeviceIndex(y)
            vendors.getCurrentDevice()
            assert vendors.getDeviceIndex() == vendors.deviceIndex
        vendors.getAPI()
    for x in range(vendors.numVendors()):
        vendors.setVendorIndex(x)
        assert vendors.getVendorIndex() == x
        assert vendors.getVendor().getName() == vendors.getCurrentVendor().getName() == vendors.vendor.getName()


def test_getlist():
    """
    Test getList() function. Must have at least one adapter driver installed to pass
    this test.
    """
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.getList() != []
    assert vendors.getList() == vendors.getVendorList()


def test_numvendors():
    """
    Test getList() function. Must have at least one adapter driver installed to pass
    this test.
    """
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.numVendors() != 0
    assert vendors.numVendors() == len(vendors.getList())


def test_vendors_and_devices():
    """
    Run through each vendor and device and make sure everything matches.
    """
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    # check vendors
    for vendorIndex in range(vendors.numVendors()):
        vendors.setVendorIndex(vendorIndex)
        assert vendors[vendorIndex] == vendors.getCurrentVendor() == vendors.getVendor() == vendors.vendor
        assert vendors.deviceIndex == 0  # setting vendor index should set device index to 0
        # check devices
        for deviceIndex in range(vendors.numDevices()):
            # check that setting by device name goes to correct index
            vendors.setDeviceIndex(deviceIndex)
            deviceID = vendors.getCurrentDevice().getID()
            assert deviceID == vendors.getDeviceID()
            vendors.setDevice(deviceID)
            assert vendors.deviceIndex == deviceIndex
            assert vendors.getCurrentDevice().getID() == deviceID
        # check that setting by api name goes to correct index
        api_name = vendors.getCurrentVendor().getAPIName()
        vendors.setVendor(api_name)
        # CMNSIM32 can sometimes be installed twice on a system
        assert vendors.vendorIndex == vendorIndex or api_name == "CMNSIM32"


def test_getVendorNames_getAPINames_getDeviceIDs():
    """Test getVendorNames(), getAPINames(), getDeviceIDs(), and __str__
    """
    vendors = RP1210.RP1210VendorList(
        RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    vendor_names = vendors.getVendorNames()
    api_names = vendors.getAPINames()

    # check if all the api_names generated by RP1210VendorList is same as API_NAMES
    assert (all(i in API_NAMES for i in api_names)
            and all(i in api_names for i in API_NAMES))
    # check if length of api_names is equal to vendor_names
    assert len(vendor_names) == len(api_names)
    # check deviceIDs
    api_vendor_names = []
    for index, value in enumerate(api_names):
        api_vendor_names.append(f'{value} - {vendor_names[index]}')
        # set vendor by vendor index indead of name
        vendors.setVendorIndex(index)
        assert value == vendors.getCurrentVendor().getAPIName() == vendors.getVendor().getAPIName()
        assert vendors.getDeviceIndex() == 0  # default device set to 0

        # check device IDs
        deviceIDs = vendors.getDeviceIDs()
        curr_vendor = vendors.getCurrentVendor()
        assert deviceIDs == curr_vendor.getDeviceIDs() == vendors.vendor.getDeviceIDs()

    # check if api - vendor is same as __str__ of RP1210VendorList
    assert ', '.join(api_vendor_names) == str(vendors) == (
        ', ').join([str(i)for i in vendors.getVendorList()])

def test_vendorlist_array():
    """Treats vendor list as a list of RP1210Config objects."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    for api_name in vendors.getAPINames():
        assert api_name in getAPINames(RP121032_PATH)
    assert len(vendors) == vendors.numVendors() == len(vendors.vendors)
    for vendor in vendors:
        assert vendor.getAPIName() in vendors.getAPINames()
    for x in range(vendors.numVendors()):
        assert vendors[x].getName() == vendors.getVendor(x).getName()

def test_vendorlist_vendor():
    """Tests the `vendor` property of VendorList."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    assert vendors.getVendorIndex() == 0
    assert vendors.vendor == vendors.getCurrentVendor()
    for vendor in vendors:
        vendors.vendor = vendor
        assert vendors.getCurrentVendor() == vendor == vendors.vendor

def test_vendorlist_setVendor_invalidType():
    """Call setVendor with invalid type."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    with pytest.raises(TypeError):
        vendors.setVendor(432452)

def test_vendorlist_setVendor_newVendor():
    """Call setVendor with vendor that isn't in list."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    api_name = "dinglebop"
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    config = RP1210.RP1210Config(api_name, dll_path, ini_path)
    vendors.setVendor(config)
    assert vendors.getAPIName() == api_name
    assert vendors.getVendorIndex() == vendors.getVendorIndex(api_name) != 0
    assert vendors.vendor == config
