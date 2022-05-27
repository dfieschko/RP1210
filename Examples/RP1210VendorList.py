import RP1210

# initialize RP1210VendorList
vendorList = RP1210.RP1210VendorList()

# print vendor information in RP121032.ini
print("List of vendors:")
for vendor in vendorList.getVendorList():
    print(f"\t{vendor}")
print(f"API Object: {vendorList.getAPI()}")
print(f"Number of vendors: {vendorList.numVendors()}")
print(f"Number of devices: {vendorList.numDevices()}")

# Connect to specific adapter
vendorList.setVendor("NULN2R32")
vendorList.setDevice("1")
vendorList.getAPI().ClientConnect(vendorList.getDeviceID())

# Connect to first adapter in list
vendorList.setVendorIndex(0)
vendorList.setDeviceIndex(0)
vendorList.getAPI().ClientConnect(vendorList.getDeviceID())

# define API_NAME and DEVICE_ID
API_NAME = "NULN2R32"
DEVICE_ID = '1'

# check if the API_NAME is in the vendor list
if API_NAME in [str(i).split(' ')[0] for i in vendorList.getVendorList()]:
    # set vendor and vendor index
    vendorList.setVendor(API_NAME)
    print(
        f"Current vendor: {vendorList.getCurrentVendor()}, name: {vendorList.getVendorName()}, index: {vendorList.getVendorIndex()}")
    print(
        f"Vendor at index 2: {vendorList.getVendor(2)}, vendor index of DG121032: {vendorList.getVendorIndex('DG121032')}")

    # check if the device is in the device list
    if DEVICE_ID in [str(i).split(' ')[0] for i in vendorList.getCurrentVendor().getDevices()]:
        # set device and device index
        vendorList.setDevice(DEVICE_ID)
        print(
            f"Current vendor's device name: {vendorList.getCurrentDevice()}, ID: {vendorList.getDeviceID()},index: {vendorList.getDeviceIndex()}")
    else:
        print("setDevice function was passed because DEVICE_ID is not in the device list")
else:
    print("setVendor and setVendorIndex functions were passed because API_NAME is not existed in .ini file")
