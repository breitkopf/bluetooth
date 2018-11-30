# Indoor location mapper using low-energy Bluetooth
# Author: Omar Metwally, MD
# omar@analog.earth
# Principal Investigator
# A N A L O G  L A B S
# License: Analog Labs (analog.earth)

from bluepy.btle import Scanner, DefaultDelegate
from time import sleep
import requests

first_scan = []
second_scan = []
signal_strength = {}
scan_targets = {} # key is ble address, value is signal strength

LOCATION_NAME = "8th floor, Elfiky Conference Room"

CURRENT_STATE = 0
SIGNAL_THRESHOLD = -65
STATE = { 0: 'Menu', 1 : 'Detect Device', 2 : 'Detect Proximity', 3 : 'Exit' }

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

        def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev:
                print("Discovered device", dev.addr)
            elif isNewData:
                print("Received new data from", dev.addr)

greeting_text = """

Bluetooth Proximity Scanner
    *    *    *    *
      *    *    *
        *    *
          *    *
    A N A L O G  L A B S

Author:   (C) 2018 Omar Metwally, MD
          omar@analog.earth
          Analog Labs, Logisome Inc R&D
License:  Analog Labs (analog.earth)
          *   *
        *    *
      *    *    *
    *    *    *    *


    """

input_text = """
What would you like to do?
Options:

1 - Register a new device
2 - Detect Proximity
3 - Exit

> """

print(greeting_text)
while True:
    if CURRENT_STATE == 0:
        CURRENT_STATE = input(input_text)
        if CURRENT_STATE.isnumeric():
            CURRENT_STATE = int(CURRENT_STATE)

    elif CURRENT_STATE == 1:
        device_name = input("Please name your phone (e.g. \"Oncology Attending\".\n\n> ")
        while True:
            confirm = input("You entered "+device_name+". Would you like to use this name? (y/N)\n> ")
            if "y" in confirm.lower():
                break
            else:
                device_name = input("Please name your phone (e.g. \"Oncology Attending\".\n> ")

        # Initial scan
        x = input("I will now scan nearby BLE devices.\nMake sure your phone has Bluetooth enabled and near the RPI.\nThis will take 10 seconds.\n\nPress ENTER to continue...\n")

        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(10)

        for dev in devices:
            #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
                #print("  %s = %s" % (desc, value))
                first_scan.append(dev.addr)
                if dev.addr not in signal_strength:
                    signal_strength[ dev.addr ] = dev.rssi

        x = input("  *  *  *\n\nReady for the second scan. This will take 10 seconds.\n\nTurn off your Bluetooth and press ENTER to continue...\n\n")

        # Second scan, with Bluetooth off
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(10)

        for dev in devices:
            #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
                #print("  %s = %s" % (desc, value))
                if dev.rssi > SIGNAL_THRESHOLD:
                    second_scan.append(dev.addr)

        #print("Length of first scan: ",len(first_scan))
        #print("Length of second scan: ",len(second_scan))

        discovered = []

        if len(first_scan) <= len(second_scan):
            print('The number of devices found during the first scan is not greater than the number of devices found during the second scan. Try again.\n')
            CURRENT_STATE = 0

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
                    if strongest_signal_addr not in scan_targets.keys():
                        scan_targets[ strongest_signal_addr ] = strongest_signal

        print('Strongest signal is ',strongest_signal,' from device address ',strongest_signal_addr)

        if len(discovered) > 0:
            print('Discovery process revealed more than one device.')
            print('Saving strongest signal ',strongest_signal,' from device ',strongest_signal_addr)
            CURRENT_STATE = 2
        elif len(discovered) == 0:
            print('Discovery process revealed no devices. Please try again.')
            CURRENT_STATE = 0

    elif CURRENT_STATE == 2:
        if len(scan_targets.keys()) == 0:
            print('No devices registerd. Please choose option 1 to register a new device.\n\n')
            CURRENT_STATE = 0
        else:
            while True:
                print('Detecting signal strength...')
                scanner = Scanner().withDelegate(ScanDelegate())
                devices = scanner.scan(10)

                for dev in devices:
                    #print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                    for (adtype, desc, value) in dev.getScanData():
                        #print("  %s = %s" % (desc, value))
                        if dev.addr == strongest_signal_addr:
                            print(dev.addr,' signal strength: ', dev.rssi)

                        if dev.addr in scan_targets.keys():
                            print('Device: ', dev.addr)
                            print('Signal strength: ', dev.rssi)

                            # upload data
                            data = { 'location_name': LOCATION_NAME, 'ble_addr': dev.addr, 'signal': dev.rssi, 'alias': device_name }
                            r = requests.post( "https://diy.analog.earth/fleetfox/default/api/bluetooth", data=data )
                            print(r.status_code, r.text)

                sleep(10)
    elif CURRENT_STATE == 3:
        print("Goodbye!\n\n  *  *  *\n")
        exit(0)
    else:
        CURRENT_STATE = 0




