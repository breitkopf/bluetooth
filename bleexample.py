from bluepy.btle import Scanner, DefaultDelegate
from time import sleep

first_scan = []
second_scan = []
signal_strength = {}

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

        def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev:
                print("Discovered device", dev.addr)
            elif isNewData:
                print("Received new data from", dev.addr)

# Initial scan
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10)

for dev in devices:
    #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        #print("  %s = %s" % (desc, value))
        first_scan.append(dev.addr)
        if dev.addr not in signal_strength:
            signal_strength[ dev.addr ] = dev.rssi

print("Now turn off Bluetooth...")
sleep(1)
x = None
while True:
    x = input('Press any key to continue: ')
    if x:
        break

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
            else:
                print(dev.addr,' is not ',strongest_signal_addr)

            if dev.addr is strongest_signal_addr:
                print('Device: ', dev.addr)
                print('Signal strength: ', dev.rssi)
    sleep(1)




