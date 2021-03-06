from ctypes import CDLL, cdll, create_string_buffer
import pytest
import RP1210, os, configparser
from utilities import RP1210ConfigTestUtility

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

def test_getAPINames():
    """
    Test the getAPINames() function with a custom directory.
    
    Also calls getAPINames() with no argument to make sure there isn't an exception.
    """
    RP1210.getAPINames()
    for name in RP1210.getAPINames(RP121032_PATH):
        assert name in API_NAMES

@pytest.mark.parametrize("rp121032_path", ["bork", "bork.ini", 1234, "RP121032", RP121032_PATH + "x"])
def test_getAPINames_invalid(rp121032_path):
    """
    Makes sure we get an exception if we provide an invalid path for getAPINames().
    """
    with pytest.raises(FileNotFoundError):
        RP1210.getAPINames(rp121032_path)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_RP1210Config(api_name : str):
    """
    Tests RP1210Config class with all sample files provided in test-files folder.
    """
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    assert rp1210.isValid() == True or api_name in INVALID_API_NAMES
    assert rp1210.getAPIName() == api_name == rp1210.api.getAPIName()
    utility.verifydata(rp1210.getName, "VendorInformation", "Name", fallback="(Vendor Name Missing)")
    utility.verifydata(rp1210.getAddress1, "VendorInformation", "Address1")
    utility.verifydata(rp1210.getAddress2, "VendorInformation", "Address2")
    utility.verifydata(rp1210.getCity, "VendorInformation", "City")
    utility.verifydata(rp1210.getState, "VendorInformation", "State")
    utility.verifydata(rp1210.getCountry, "VendorInformation", "Country")
    utility.verifydata(rp1210.getPostal, "VendorInformation", "Postal")
    utility.verifydata(rp1210.getTelephone, "VendorInformation", "Telephone")
    utility.verifydata(rp1210.getFax, "VendorInformation", "Fax")
    utility.verifydata(rp1210.getVendorURL, "VendorInformation", "VendorURL")
    utility.verifydata(rp1210.getVersion, "VendorInformation", "Version")
    utility.verifydata(rp1210.autoDetectCapable, "VendorInformation", "AutoDetectCapable", fallback=False)
    utility.verifydata(rp1210.getAutoDetectCapable, "VendorInformation", "AutoDetectCapable", fallback=False)
    utility.verifydata(rp1210.getTimeStampWeight, "VendorInformation", "TimeStampWeight", fallback=1.0)
    utility.verifydata(rp1210.getMessageString, "VendorInformation", "MessageString")
    utility.verifydata(rp1210.getErrorString, "VendorInformation", "ErrorString")
    utility.verifydata(rp1210.getRP1210Version, "VendorInformation", "RP1210")
    utility.verifydata(rp1210.getDebugLevel, "VendorInformation", "DebugLevel", fallback=-1)
    utility.verifydata(rp1210.getDebugFile, "VendorInformation", "DebugFile")
    utility.verifydata(rp1210.getDebugMode, "VendorInformation", "DebugMode", fallback=-1)
    utility.verifydata(rp1210.getDebugFileSize, "VendorInformation", "DebugFileSize", fallback=1024)
    utility.verifydata(rp1210.getNumberOfSessions, "VendorInformation", "NumberOfRTSCTSSessions", fallback=1)
    utility.verifydata(rp1210.getCANAutoBaud, "VendorInformation", "CANAutoBaud", fallback=False)
    utility.verifydata(rp1210.getCANFormatsSupported, "VendorInformation", "CANFormatsSupported")
    utility.verifydata(rp1210.getJ1939FormatsSupported, "VendorInformation", "J1939FormatsSupported")
    utility.verifydata(rp1210.getDeviceIDs, "VendorInformation", "Devices")
    utility.verifydata(rp1210.getProtocolIDs, "VendorInformation", "Protocols")
    assert rp1210.getName() == rp1210.getDescription()
    assert rp1210.getName() in str(rp1210)
    assert rp1210.getCANAutoBaud() == rp1210.autoBaudEnabled()
    assert rp1210.getProtocol() == rp1210.getProtocol("J1939")

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_RP1210Config_forceempty(api_name : str):
    """
    Test behavior after RP1210Config is forcibly cleared.
    
    This is here to test for cases where RP1210Config is missing sections.

    I was hoping this would cover the exceptions in RP1210Config, but it doesn't :(
    """
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    rp1210.clear()
    assert rp1210.getDevices() == []
    assert rp1210.getProtocols() == []
    assert rp1210.getProtocolNames() == []
    assert rp1210.getProtocolIDs() == []

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_Devices(api_name : str):
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    deviceIDs = rp1210.getDeviceIDs()
    for id in deviceIDs:
        device = rp1210.getDevice(id)
        utility.verifydevicedata(device.getID, id, "DeviceID", fallback=-1)
        utility.verifydevicedata(device.getDescription, id, "DeviceDescription")
        utility.verifydevicedata(device.getName, id, "DeviceName")
        utility.verifydevicedata(device.getParams, id, "DeviceParams")
        utility.verifydevicedata(device.getMultiJ1939Channels, id, "MultiJ1939Channels", fallback=0)
        utility.verifydevicedata(device.getMultiCANChannels, id, "MultiCANChannels", fallback=0)
        if device.getID() == -1:
            assert "(Invalid Device)" in str(device)
        else:
            assert str(device) == str(device.getID()) + " - " + device.getDescription()
        assert device in rp1210.getDevices()
        with pytest.raises(TypeError):
            assert device != "dingus"

@pytest.mark.parametrize("api_name", argvalues=API_NAMES + INVALID_API_NAMES)
def test_Protocols(api_name : str):
    config = configparser.ConfigParser()
    utility = RP1210ConfigTestUtility(config)
    rp1210 = RP1210.RP1210Config(api_name, DLL_DIRECTORY, INI_DIRECTORY)
    config.read(INI_DIRECTORY + "\\" + api_name + ".ini")
    protocolIDs = rp1210.getProtocolIDs()
    assert rp1210.getProtocol("test protocol name") is None
    assert rp1210.getProtocol([]) is None
    for name in rp1210.getProtocolNames():
        assert rp1210.getProtocol(name).getString() == name
    assert not rp1210.getProtocol("dinglebop protocol")
    assert not rp1210.getProtocol(b"this is bytes, not int or str")
    if not api_name in invalid_apis:
        assert rp1210.getProtocolNames()
    if not api_name in INVALID_API_NAMES:
        assert protocolIDs
    if api_name in INVALID_API_NAMES and api_name != "invalid_pd_api":
        assert rp1210.getProtocols() == []
    for id in protocolIDs:
        protocol = rp1210.getProtocol(id)
        name = protocol.getString()
        protocolFromString = rp1210.getProtocol(name)
        assert protocolFromString.getString() == name
        assert name in rp1210.getProtocolNames()
        assert rp1210.getProtocol(name).getString() == name
        utility.verifyprotocoldata(protocol.getDescription, id, "ProtocolDescription")
        utility.verifyprotocoldata(protocol.getString, id, "ProtocolString")
        utility.verifyprotocoldata(protocol.getParams, id, "ProtocolParams")
        utility.verifyprotocoldata(protocol.getDevices, id, "Devices")
        utility.verifyprotocoldata(protocol.getSpeed, id, "ProtocolSpeed")
        assert protocol in rp1210.getProtocols()
        with pytest.raises(TypeError):
            assert protocol != "dingus"

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_load_DLL(api_name : str):
    """Loads an API's DLL and checks for validity."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    # try to load it twice, to make sure they don't collide or something
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert rp1210.getAPI().isValid()
    assert rp1210.api.getDLL() != None
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert rp1210.api.loadDLL() != None
    # make sure that RP1210API is invalid if DLL is set to None
    rp1210.api.setDLL(None)
    assert not rp1210.api._api_valid

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_conformsToRP1210C(api_name : str):
    """Tests conformsToRP1210C function."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    if not rp1210.api.isValid():
        assert not rp1210.api.conformsToRP1210C()
    if rp1210.api.isValid():
        assert rp1210.api.conformsToRP1210C() == rp1210.api._conforms_to_rp1210c

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ClientConnect(api_name : str):
    """Tests whether ClientConnect follows expected behavior when disconnected from device."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    deviceID = rp1210.getProtocol("J1939").getDevices()[0]
    clientID = rp1210.api.ClientConnect(deviceID, b"J1939:Baud=Auto")
    assert RP1210.translateErrorCode(clientID) in RP1210.RP1210_ERRORS.values()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ClientDisconnect(api_name : str):
    """Tests whether ClientDisconnect follows expected behavior when disconnected from device."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    code = rp1210.api.ClientDisconnect(0)
    if code < 0:
        code += 65536
    if api_name == "NULN2R32": # Nexiq drivers can trick computer into thinking it's connected
        assert code == 0 or code >= 128
        return
    assert code >= 128

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadVersion(api_name : str):
    """Test RP1210_ReadVersion while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadVersion test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buff1 = create_string_buffer(16)
    buff2 = create_string_buffer(16)
    buff3 = create_string_buffer(16)
    buff4 = create_string_buffer(16)
    rp1210.api.ReadVersion(buff1, buff2, buff3, buff4)
    assert str(buff1) + str(buff2) + str(buff3) + str(buff4) != ""

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadVersionDirect(api_name : str):
    """Test ReadVersionDirect while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadVersionDirect test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    dll_ver, api_ver = rp1210.api.ReadVersionDirect()
    assert dll_ver != ""
    assert api_ver != ""
    assert dll_ver == rp1210.api.ReadDLLVersion()
    assert api_ver == rp1210.api.ReadAPIVersion()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_ReadDetailedVersion(api_name : str):
    """Test ReadDetailedVersion while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping ReadDetailedVersion test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buff1 = create_string_buffer(17)
    buff2 = create_string_buffer(17)
    buff3 = create_string_buffer(17)
    ret_val = rp1210.api.ReadDetailedVersion(0, buff1, buff2, buff3)
    assert RP1210.translateErrorCode(ret_val) in ["ERR_DLL_NOT_INITIALIZED", "ERR_HARDWARE_NOT_RESPONDING", "ERR_INVALID_CLIENT_ID"]
    assert rp1210.api.ReadDetailedVersionDirect(0)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetErrorMsg(api_name : str):
    """Test GetErrorMsg while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetErrorMsg test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for code in RP1210.RP1210_ERRORS.keys():
        msg = rp1210.api.GetErrorMsg(code)
        if not api_name == "DrewLinQ": # DrewLinQ fails this, but that's their problem
            assert msg != ""

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_SendCommand(api_name : str):
    """Test SendCommand while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping SendCommand test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for command in RP1210.RP1210_COMMANDS:
        assert RP1210.translateErrorCode(rp1210.api.SendCommand(command, 0)) in RP1210.RP1210_ERRORS.values()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetHardwareStatus(api_name : str):
    """Test GetHardwareStatus while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetHardwareStatus test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    buffer = create_string_buffer(64)
    ret_val = rp1210.api.GetHardwareStatus(0, buffer, 64)
    if ret_val < 0:
        ret_val += 65536
    assert not buffer.value
    assert ret_val in RP1210.RP1210_ERRORS

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_GetHardwareStatusDirect(api_name : str):
    """Test GetHardwareStatusDirect while adapter is disconnected."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping GetHardwareStatusDirect test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert not int.from_bytes(rp1210.api.GetHardwareStatusDirect(0), 'big')

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_SendMessage(api_name : str):
    if api_name in invalid_apis:
        pytest.skip(f"Skipping SendMessage test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    for val in ["blargle", "", 0, 324234, b'blargle', b'']:
        ret_val = rp1210.api.SendMessage(0, val) # set size automatically
        assert RP1210.translateErrorCode(ret_val) in RP1210.RP1210_ERRORS.values()
        if not isinstance(val, int):
            ret_val = rp1210.api.SendMessage(0, val, len(val)) # specify size
            assert RP1210.translateErrorCode(ret_val) in RP1210.RP1210_ERRORS.values()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_disconnected_Read(api_name : str):
    """Test ReadMessage and ReadDirect."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping 'Remaining Functions' test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    rp1210 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    read_array_in = create_string_buffer(256)
    assert rp1210.api.ReadMessage(128, read_array_in, len(read_array_in)) <= 0
    assert not read_array_in.value
    read_array_in = create_string_buffer(64)
    assert rp1210.api.ReadMessage(0, read_array_in) <= 0
    assert not read_array_in.value
    assert not rp1210.api.ReadDirect(0)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210API_magic_methods(api_name : str):
    """Test __bool__ and __str__ in RP1210API."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping 'Remaining Functions' test for {api_name} due to missing dependencies.")
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    api = RP1210.RP1210API(api_name, dll_path)
    assert bool(api) == api.isValid()
    assert str(api) == api.getAPIName()

@pytest.mark.parametrize("api_name", argvalues=INVALID_API_NAMES)
def test_RP1210API_magic_methods_with_invalid_api(api_name : str):
    """Test __bool__ and __str__ in RP1210API with invalid API names."""
    api = RP1210.RP1210API(api_name)
    assert bool(api) == api.isValid()
    assert str(api) == api.getAPIName()

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210Config_magic_methods(api_name : str):
    """Test __bool__ in RP1210Config."""
    if api_name in invalid_apis:
        pytest.skip(f"Skipping 'Remaining Functions' test for {api_name} due to missing dependencies.")
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    config = RP1210.RP1210Config(api_name, dll_path, ini_path)
    config2 = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert bool(config) == config.isValid()
    assert config == config2
    if api_name != "NULN2R32":
        assert config != RP1210.RP1210Config("NULN2R32", dll_path, ini_path)

@pytest.mark.parametrize("api_name", argvalues=INVALID_API_NAMES)
def test_RP1210Config_magic_methods_with_invalid_api(api_name : str):
    """Test __bool__ in RP1210Config with invalid API names."""
    config = RP1210.RP1210Config(api_name)
    config2 = RP1210.RP1210Config(api_name)
    assert bool(config) == config.isValid()
    assert config == config2
    assert config != RP1210.RP1210Config("dinglebop")

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210VendorList_addVendor(api_name : str):
    """Tests addVendor function in RP1210VendorList"""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    config = RP1210.RP1210Config(api_name, dll_path, ini_path)
    assert config in vendors
    assert RP1210.RP1210Config("dinglebop") not in vendors
    # add by name
    length = len(vendors)
    vendors.addVendor(api_name)
    assert len(vendors) == length + 1
    assert vendors[length] == config
    # add by RP1210Config object
    vendors.addVendor(config)
    assert len(vendors) == length + 2
    assert vendors[length + 1] == config
    # add random api name
    vendors.addVendor("dinglebop")
    assert len(vendors) == length + 3
    assert vendors[length + 2] != config
    assert not vendors[length + 2].isValid() # should be invalid
    # add invalid type
    with pytest.raises(TypeError):
        vendors.addVendor(4)

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210VendorList_setVendorByName(api_name : str):
    """Tests setVendor function in RP1210VendorList"""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    config = RP1210.RP1210Config(api_name, dll_path, ini_path)
    vendors.setVendor(api_name)
    assert vendors.getAPIName() == api_name
    assert vendors.getVendorIndex() == vendors.getVendorIndex(api_name)
    assert vendors.vendor == config

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210VendorList_setVendorByVendor(api_name : str):
    """Tests setVendor function in RP1210VendorList"""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    ini_path = INI_DIRECTORY + "\\" + api_name + ".ini"
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    config = RP1210.RP1210Config(api_name, dll_path, ini_path)
    vendors.setVendor(config)
    assert vendors.getAPIName() == api_name
    assert vendors.getVendorIndex() == vendors.getVendorIndex(api_name)
    assert vendors.vendor == config

@pytest.mark.parametrize("api_name", argvalues=API_NAMES)
def test_RP1210VendorList_accessAPI(api_name : str):
    """Access `api` property in RP1210VendorList."""
    vendors = RP1210.RP1210VendorList(RP121032_PATH, DLL_DIRECTORY, INI_DIRECTORY)
    dll_path = DLL_DIRECTORY + "\\" + api_name + ".dll"
    api = RP1210.RP1210API(api_name, dll_path)
    vendors.setVendor(api_name)
    assert vendors.api == api == api_name
    assert vendors.getAPIName() == vendors.api.getAPIName()
    # setter should raise exception
    with pytest.raises(AttributeError):
        vendors.api = api
