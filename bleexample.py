# Indoor location mapper using low-energy Bluetooth
# Author: Omar Metwally, MD
# omar@analog.earth
# Principal Investigator
# A N A L O G  L A B S
# License: Analog Labs (analog.earth)

from bluepy.btle import Scanner, DefaultDelegate
from time import sleep

first_scan = []
second_scan = []
signal_strength = {}

LOCATION_NAME = "8th floor, Elfiky Conference Room"

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

        def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev:
                print("Discovered device", dev.addr)
            elif isNewData:
                print("Received new data from", dev.addr)

device_name = input("Please name your phone (e.g. \"Oncology Attending\".\n\n")
while True:
    confirm = input("You entered "+device_name+". Would you like to use this name?")
    if "y" in confirm.lower():
        break
    else:
        device_name = input("Please name your phone (e.g. \"Oncology Attending\".\n\n")

# Initial scan
x = input("I will now scan nearby BLE devices.\n\nMake sure your phone has Bluetooth enabled and near the RPI.\n\nThis will take 10 seconds.\n\nPress ENTER to continue...")

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10)

for dev in devices:
    #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        #print("  %s = %s" % (desc, value))
        first_scan.append(dev.addr)
        if dev.addr not in signal_strength:
            signal_strength[ dev.addr ] = dev.rssi

x = input("Ready for the second scan. This will take 10 seconds.\n\nTurn off your Bluetooth and press ENTER to continue...")

# Second scan, with Bluetooth off
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10)

for dev in devices:
    #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        #print("  %s = %s" % (desc, value))
        second_scan.append(dev.addr)

#print("Length of first scan: ",len(first_scan))
#print("Length of second scan: ",len(second_scan))

discovered = []

if len(first_scan) <= len(second_scan):
    print('The number of devices found during the first scan is not greater than the number of devices found during the second scan. Try again.')
    exit(0)

for dev in first_scan:
    if dev not in second_scan:
        if dev not in discovered:
            discovered.append(dev)

print('Discovered devices: ',discovered)
for d in discovered:
    print(d, signal_strength[d])

# identify device address with strongest signal
strongest_signal_addr = None
strongest_signal = None

print('enumerating signal_strength')
for addr, signal in signal_strength.items():
    print(addr,signal)
    if not strongest_signal:
        strongest_signal_addr = addr
        strongest_signal = signal
    else:
        if signal > strongest_signal:
            strongest_signal = signal
            strongest_signal_addr = addr

print('Strongest signal is ',strongest_signal,' from device address ',strongest_signal_addr)

if len(discovered) > 1:
    print('Discovery process revealed more than one device.')
    print('Remembering strongest signal ',strongest_signal,' from device ',strongest_signal_addr)
elif len(discovered) == 0:
    print('Discovery process revealed no devices. Please try again.')
    exit(0)

while True:
    print('updating signal strength...')
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10)

    for dev in devices:
        #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            #print("  %s = %s" % (desc, value))
            if dev.addr == strongest_signal_addr:
                print(dev.addr,' signal strength: ', dev.rssi)

            if dev.addr is strongest_signal_addr:
                print('Device: ', dev.addr)
                print('Signal strength: ', dev.rssi)
    sleep(1)




